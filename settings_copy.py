import os
from typing import List, Dict

import numpy
from dotenv import load_dotenv

from repos.repo_types import CropParams

ROOT_PATH: str = os.path.dirname(os.path.abspath(__file__))

env_path: str = os.path.join(ROOT_PATH, ".env")
load_dotenv(env_path)


BIN_PATH: str = ""
METEO_BASE_PHOTO_URL: str = (
    "http://www.meteo.pl/um/metco/leg_um_pl_cbase_256.png"  # noqa
)
MEDIA: str = os.path.join(ROOT_PATH, "media")
BOT_NAME: str = ""

TOKEN: str = os.getenv("DISCORD_TOKEN")
GUILD: str = os.getenv("DISCORD_GUILD")

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

if not os.path.exists(MEDIA):
    os.mkdir(MEDIA)

LOGS_PATH: str = os.path.join(ROOT_PATH, "logs")
DISCORD_LOGS: str = "logs/discord/{date}.log"

if not os.path.exists(LOGS_PATH):
    os.mkdir(LOGS_PATH)

DB_CONFIG: dict = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": os.getenv("HOST", "localhost"),
                "port": os.getenv("PORT", 5432),
                "user": os.getenv("USER", "postgres"),
                "password": os.getenv("PASSWORD", "postgres"),
                "database": os.getenv("DATABASE_NAME", "postgres"),
            },
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

CHANNELS: Dict[str, int] = {}


try:
    from _local_settings import *
except Exception as e:
    print(f"No local settings. {e}")

matrix = numpy.fromfile(os.path.join(ROOT_PATH, BIN_PATH))
MATRIX_RESHAPE = numpy.reshape(matrix, (616, 448, 2))
