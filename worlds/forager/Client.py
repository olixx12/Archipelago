import asyncio
import Utils
import websockets
import functools
from copy import deepcopy
from typing import Iterable
from NetUtils import decode, encode, JSONtoTextParser, JSONMessagePart, NetworkItem, NetworkPlayer
from MultiServer import Endpoint
from CommonClient import CommonContext, gui_enabled, ClientCommandProcessor, logger, get_base_parser, server_loop
import aiohttp.web

DEBUG = True

class ForagerJSONToTextParser(JSONtoTextParser):
    def _handle_color(self, node: JSONMessagePart):
        return self._handle_text(node)  # No colors for the in-game text



class ForagerContext(CommonContext):
    command_processor = ClientCommandProcessor
    game = "Forager"

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.http_task = None
        self.gamejsontotext = ForagerJSONToTextParser(self)
        self.autoreconnect_task = None
        self.endpoint = None
        self.items_handling = 0b111
        self.room_info = None
        self.connected_msg = None
        self.game_connected = False
        self.awaiting_info = False
        self.full_inventory: list[any] = []
        self.server_msgs: list[any] = []

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(ForagerContext, self).server_auth(password_requested)

        await self.get_username()
        await self.send_connect()

    async def disconnect(self, allow_autoreconnect: bool = False):
        await super().disconnect(allow_autoreconnect)


    def is_connected(self) -> bool:
        return self.server and self.server.socket.open

    def on_print_json(self, args: dict):
        text = self.gamejsontotext(deepcopy(args["data"]))
        msg = {"cmd": "PrintJSON", "data": [{"text": text}], "type": "Chat"}
        self.server_msgs.append(encode([msg]))

        if self.ui:
            self.ui.print_json(args["data"])
        else:
            text = self.jsontotextparser(args["data"])
            logger.info(text)

    def update_items(self):
        # just to be safe - we might still have an inventory from a different room
        if not self.is_connected():
            return

        self.server_msgs.append(encode([{"cmd": "ReceivedItems", "index": 0, "items": self.full_inventory}]))

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)  # Import to ensure Universal Tracker gets the required information it needs.
        if cmd == "Connected":
            json = args
            # This data is not needed and causes the game to freeze for long periods of time in large asyncs.
            if "slot_info" in json.keys():
                json["slot_info"] = {}
            if "players" in json.keys():
                me: NetworkPlayer
                for n in json["players"]:
                    if n.slot == json["slot"] and n.team == json["team"]:
                        me = n
                        break

                # Only put our player info in there as we actually need it
                json["players"] = [me]
            if DEBUG:
                print(json)
            self.connected_msg = encode([json])
            if self.awaiting_info:
                self.server_msgs.append(self.room_info)
                self.update_items()
                self.awaiting_info = False

        elif cmd == "RoomUpdate":
            # Same story as above
            json = args
            if "players" in json.keys():
                json["players"] = []

            self.server_msgs.append(encode(json))

        elif cmd == "ReceivedItems":
            if args["index"] == 0:
                self.full_inventory.clear()

            for item in args["items"]:
                self.full_inventory.append(NetworkItem(*item))

            self.server_msgs.append(encode([args]))

        elif cmd == "RoomInfo":
            self.seed_name = args["seed_name"]
            self.room_info = encode([args])

        else:
            if cmd != "PrintJSON":
                self.server_msgs.append(encode([args]))

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = "Archipelago Forager Client"
        return ui
    
    async def locationHandler(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        requestjson = await request.json()
        logger.info(requestjson)
        try:
            await self.check_locations(requestjson["Locations"])
        except:
            pass
        localResponse = aiohttp.web.json_response({"message": "This is a placeholder JSON response."},status=200)
        return localResponse
    
    async def itemsHandler(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """handle GET at /Items"""
        response = self.build_item_response()
        return aiohttp.web.json_response(response)
    
    def build_item_response(self):
        """
        expected return value to be like:
        {"Gear" : {"pickaxe" : 3, "sword" : 2}, "Skills" : [0,1,0,0,1,...]}
        "Skills is a 64 long array" 
        """
        skills = [0 for i in range(64)]
        gear = {}
        for item in self.items_received:
            if(item[0] >= 300 and item[0] < 364):
                skills[item[0] - 300] = 1
            elif(item[0] >= 249 and item[0] <= 260):
                name = self.item_names["Forager"][item[0]]
                name = name[12:].lower()
                gear[name] = gear.get(name,0) + 1
        itemmessage = {
            "Gear" : gear,
            "Skills" : skills
        }
        return itemmessage




def launch():
    async def main():
        from .Server import ArchiHandler, http_server_loop
        parser = get_base_parser()
        args = parser.parse_args()

        ctx = ForagerContext(args.connect, args.password)
        logger.info("Starting the Forager proxy server")
        server = ArchiHandler(ctx)
        ctx.httpServer_task = asyncio.create_task(http_server_loop(server), name="http server loop")
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()
        await ctx.shutdown()
    Utils.init_logging("ForagerClient")
    asyncio.run(main())