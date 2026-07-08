from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
from urllib.parse import urlparse, parse_qs
import asyncio
from aiohttp import web

from .Client import ForagerContext
from CommonClient import logger


gear_index = {
    "pickaxe": 0,
    "shovel": 1,
    "sword": 2,
    "bow": 3,
    "lightning": 4,
    "ice": 5,
    "fire": 6,
    "amulet": 7,
    "boot": 8,
    "glove": 9,
    "book": 10,
    "backpack" : 11,
    "wallet" : 12,
    "nerdy_glasses": 13,
    "top_hat" : 14,
    "pink_bow" : 15,
    "lantern" : 16,
    "skull_key" : 17,
    "skeleton_mask" : 18,
    "fairy_aura" : 19,
    "quiver" : 20,
    "vampire_wings" : 21,
    "shield" : 22,
    "magic_scepter" : 23,
    "holy_relic": 24,
    "ancient" : 25,
    "fire" : 26,
    "frozen_galaxy":27,
    "skull":28,
    "ancient_galaxy":29,
    "fire_galaxy":30,
    "frozen_galaxy":31,
    "skull_galaxy":32,
    "museum": 33,
    "death": 34,
    "obliterator": 35,
    "fish_net" : 36,
    "merchant_medallion" : 37,
    "lunar_medalion": 38,
    "hammer": 39,
    "fishing": 40
}

skill_index = {
    "industry" : 0,
    "capentry" : 1,
    "masonry": 2,
    "machinery" : 3,
    "sewing": 4,
    "craftsmenship": 5,
    "manufacturing": 6,
    "drilling": 7,
    "textiles" : 8,
    "smelting" : 9,
    "railroads" : 10,
    "automation": 11,
    "jewlery": 12,
    "physics": 13,
    "engineering": 14,
    "lasers": 15,
    "economy" : 16,
    "storage" : 17,
    "gambling" : 18,
    "optics": 19,
    "trade" : 20,
    "banking" : 21,
    "management" : 22,
    "architecture" : 23,
    "bargin" :24,
    "capitalsim" : 25,
    "treasury" : 26,
    "autorepair": 27,
    "supply": 28,
    "artistry": 29,
    "colonization" : 30,
    "logistics" : 31,
    "foraging" : 32,
    "gathering" : 33,
    "farming" : 34,
    "pet": 35,
    "hunting" :36,
    "fishing" : 37,
    "mining" : 38,
    "geology" : 39,
    "ballistics" : 40,
    "cooking" : 41,
    "calciverous" : 42,
    "prospecting" : 43,
    "looting" : 44,
    "gluttony": 45,
    "prowess" : 46,
    "deposit" : 47,
    "magic" : 48,
    "alchemy": 49,
    "inscription" : 50,
    "thaumaturgy" : 51,
    "combat" : 52,
    "evasion" : 53,
    "reagency" : 54,
    "faith" : 55,
    "renewal" : 56,
    "spellbind" : 57,
    "transmutation" : 58,
    "conjuration" : 59,
    "destruction" : 60,
    "spirituality" : 61,
    "summoning" : 62,
    "astrology" : 63
}

shared_data = {
    "global_gears" : [114, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, 148, 154, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4],
    "global_level": 1,
    "global_skills" : [1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
    "archi_level" : 1,
    "archi_gears" : [114, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, 148, 154, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4],
    "archi_skills": [1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
    "forager_gears": [114, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, 148, 154, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4],
    "forager_level": 1,
    "forager_skills": [1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
    "foragerHasUpdate": False,
    "archiHasUpdate": False,
}


class ArchiHandler:
    def __init__(self, ctx: ForagerContext):
        self.app = web.Application()
        self.host = "localhost"
        self.port = "8000"
        self.ctx = ctx

        self.connected = False

    async def initializer(self) -> web.Application:
        self.app.router.add_post('/Locations', self.ctx.locationHandler)
        self.app.router.add_post('/Goal', self.ctx.goalHandler)
        #self.app.router.add_post('/Death', self.ctx.deathHandler)
        #self.app.router.add_get('/Deathpoll', self.ctx.deathpollHandler)
        self.app.router.add_get('/Items', self.ctx.itemsHandler)
        self.app.router.add_get('/Datapackage', self.ctx.datapackageHandler)
        #self.app.router.add_get('/ErConnections', self.ctx.erConnHandler)
        return self.app

    async def my_run_app(self, app, host, port):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        while True:
            await asyncio.sleep(3600)  # sleep forever

    async def run(self):
        if not self.connected:
            await self.my_run_app(
                app=await self.initializer(),
                host=self.host, port=self.port
                )
            self.connected = True
            return self.connected
        else:
            logger.info('Already connected')
            return


async def http_server_loop(wb: ArchiHandler) -> None:
    try:
        logger.info('Trying to launch http server')
        await wb.run()
    finally:
        logger.info('http_server_loop ended')

#if __name__ == '__main__':
#    ctx = ForagerContext("localhost", "")
#    webserver = Webserver(ctx)
#    webserver.run()