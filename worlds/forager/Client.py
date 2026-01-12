import asyncio
import time

import Utils
import websockets
import functools
from CommonClient import CommonContext, gui_enabled, ClientCommandProcessor, logger


class ForagerContext(CommonContext):
    game = "forager"

    def __init__(self, server_address = None, password = None):
        super().__init__(server_address, password)
        self.proxy = None
    async def server_auth(self, password_requested = False):
        if password_requested and not self.password:
            await super(ForagerContext,self).server_auth(password_requested) #TODO
        await self.get_username()
        await self.send_connect()

def proxy(websocket, path: str = "/", ctx: ForagerContext = None):
    pass
def proxy_loop(ctx: ForagerContext):
    pass
def launch(*launch_args: str):
    import colorama
    async def main():
        parser = get_base_parser()
        args = parser.parse_args(launch_args)
        ctx = ForagerContext(args.connect,args.password)
        ctx.proxy = websockets.serve(functools.partial(proxy, ctx=ctx),
                                     host="localhost", port=8000, ping_timeout=999999, ping_interval=999999)
        ctx.proxy_task = asyncio.create_task(proxy_loop(ctx), name="ProxyLoop")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.proxy
        await ctx.proxy_task
        await ctx.exit_event.wait()
    colorama.just_fix_windows_console()
    asyncio.run(main())
    colorama.deinit()