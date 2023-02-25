import asyncio
from asyncio import AbstractEventLoop
from datetime import datetime
from time import sleep

from asyncpg import CannotConnectNowError
from tortoise import Tortoise

from settings import Settings
from utils.exceptions import DBConnectionError

settings: Settings = Settings()


class DBConnectionHandler:
    """Handler responsible for connection and disconnection to database"""

    async def __aenter__(self) -> None:
        """Open database connection"""
        await Tortoise.init(config=settings.db_config)
        while True:
            retry: int = 0
            try:
                if retry >= 5:
                    raise DBConnectionError()
                await Tortoise.generate_schemas()
                break
            except (ConnectionError, CannotConnectNowError):
                retry += 1
                pass

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close database connection"""
        await Tortoise.close_connections()


#
# async def start_db():
#     await Tortoise.init(config=DB_CONFIG)
#     await Tortoise.generate_schemas()
#
#
# async def add_moon():
#     await Tortoise.init(config=DB_CONFIG)
#     await Tortoise.generate_schemas()
#     await MoonModel.create(date=datetime.now(), image=b'binary_data_here', name='dwdwdw Moon')
#
#
# async def close_db():
#     await Tortoise.close_connections()
#
#
# def aj():
#     async def main():
#
#         await start_db()
#         await add_moon()
#         await close_db()
#     loop: AbstractEventLoop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#
# # aj()
#
# async def run():
#     await Tortoise.init(config=DB_CONFIG)
#     await Tortoise.generate_schemas()
#     a: MoonModel = await MoonModel.create(date=datetime.now(), image='base.png', name='NOWEEEEE Moon')
#     breakpoint()
#     b = await MoonModel.get(id=2)
#     breakpoint()
#     await Tortoise.close_connections()

# asyncio.run(run())
