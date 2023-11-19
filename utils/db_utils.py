from asyncpg import CannotConnectNowError
from tortoise import Tortoise

from logger import ColoredLogger, get_module_logger
from settings import settings
from utils.exceptions import DBConnectionError

logger: ColoredLogger = get_module_logger("DB_UTILS")


class DBConnectionHandler:
    """Handler responsible for connection and disconnection to database"""

    async def __aenter__(self) -> None:
        """Open database connection"""
        await Tortoise.init(config=settings.db_config())
        retry: int = 0
        continue_loop: bool = True

        while continue_loop:
            try:
                logger.info(f"Trying to connect to database. Retrying: {retry} time")
                if retry >= 5:
                    logger.critical("Cannot connect to database")
                    continue_loop = False
                    raise DBConnectionError()
                logger.info(f"Connected to db {settings.db.NAME}")
                await Tortoise.generate_schemas()
                break
            except (ConnectionError, CannotConnectNowError):
                retry += 1
                pass

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close database connection"""
        await Tortoise.close_connections()
