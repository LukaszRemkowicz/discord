import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Protocol

import numpy
import sentry_sdk
from dotenv import find_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from repos.repo_types import CropParams


class DBProtocol(Protocol):
    """Database protocol"""

    def config(self, credentials: dict) -> dict:
        raise NotImplementedError


@dataclass
class TortoiseConfig:
    @staticmethod
    def config(credentials: dict) -> dict:
        return {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": credentials,
                },
            },
            "apps": {
                "models": {
                    "models": ["__main__", "repos.models", "aerich.models"],
                    "default_connection": "default",
                },
            },
            "default_connection": "default",
        }


class DatabaseSettings(BaseSettings):
    """Database settings"""

    HOST: str = "localhost"
    PORT: int = 5432
    USERNAME: str = "postgres"
    PASSWORD: SecretStr = SecretStr("postgres")
    NAME: str = "postgres"

    def credentials(self) -> dict:
        return {
            "host": self.HOST,
            "port": self.PORT,
            "user": self.USERNAME,
            "password": self.PASSWORD.get_secret_value(),
            "database": self.NAME,
        }


class UMSettings(BaseSettings):
    BASE_PHOTO: Path = Path("utils") / "base.png"


class SentrySettings(BaseSettings):
    """Sentry settings"""

    dsn: str


class Settings(BaseSettings):
    um: UMSettings = UMSettings()
    ROOT_PATH: str = os.path.dirname(os.path.abspath(__file__))
    METEO_BASE_PHOTO_URL: str = (
        "http://www.meteo.pl/um/metco/leg_um_pl_cbase_256.png"  # noqa
    )
    MEDIA: str = os.path.join(ROOT_PATH, "media")
    BOT_NAME: str
    DISCORD_TOKEN: str
    DISCORD_GUILD: str = ""
    BOT_PREFIX: str = "!"
    CHROME_DRIVER_OPTIONS: List[str] = [
        "--headless",
        "--window-size=1500x2000",
        "--hide-scrollbars",
    ]
    METEO_CROP: CropParams = CropParams(top=200, right=400, bottom=2000, left=2200)
    CLEAR_CROP: CropParams = CropParams(top=170, right=250, bottom=1350, left=1450)
    UM_CROP: CropParams = CropParams(top=0, right=0, bottom=820, left=660)
    MOON_CROP: CropParams = CropParams(left=230, top=290, right=1250, bottom=950)
    MOON_END_DATE_RANGE: str = "31/01/2024"
    EXEC_CHROME_PATH: str = os.path.join(
        ROOT_PATH, "chromedriver_win32", "chromedriver.exe"
    )
    LOGS_PATH: str = os.path.join(ROOT_PATH, "logs")
    DISCORD_ON_ERROR_LOGS: str = "logs/discord/{date}.log"
    db: DatabaseSettings = DatabaseSettings()
    CHANNELS: dict = {}
    sentry: SentrySettings
    environment: str
    temp_file_name: str = "temporary_image.png"

    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    MATRIX_PATH: str = ""
    MATRIX_RESHAPE: numpy.ndarray | None = None

    if os.path.isfile(MATRIX_PATH):
        MATRIX_RESHAPE: numpy.ndarray = numpy.reshape(
            numpy.fromfile(MATRIX_PATH), (616, 448, 2)
        )

    def db_config(self) -> dict:
        return TortoiseConfig.config(self.db.credentials())


settings = Settings()

# prepare media folder
if not Path(settings.MEDIA).exists():
    os.mkdir(settings.MEDIA)

# prepare logs folder
if not Path(settings.LOGS_PATH).exists():
    os.mkdir(settings.LOGS_PATH)


sentry_sdk.init(
    dsn=settings.sentry.dsn,
    traces_sample_rate=1.0,
    environment=settings.environment,
)
