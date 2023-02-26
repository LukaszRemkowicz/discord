import os
from typing import List

import numpy
from dotenv import load_dotenv

from repos.types import CropParams


class Settings:
    def __init__(self):

        self._settings = {}
        self.ROOT_PATH: str = os.path.dirname(os.path.abspath(__file__))

        env_path: str = os.path.join(self.ROOT_PATH, ".env")
        load_dotenv(env_path)

        self._settings["BIN_PATH"]: str = ""
        self._settings["ROOT_PATH"]: str = self.ROOT_PATH
        self._settings[
            "METEO_BASE_PHOTO_URL"
        ]: str = "http://www.meteo.pl/um/metco/leg_um_pl_cbase_256.png"  # noqa
        self._settings["MEDIA"]: str = os.path.join(self.ROOT_PATH, "media")
        self._settings["BOT_NAME"]: str = ""
        self._settings["TOKEN"]: str = os.getenv("DISCORD_TOKEN")
        self._settings["GUILD"]: str = os.getenv("DISCORD_GUILD")
        self._settings["CHROME_DRIVER_OPTIONS"]: List[str] = [
            "--headless",
            "--window-size=1500x2000",
            "--hide-scrollbars",
        ]
        self._settings["METEO_CROP"]: CropParams = CropParams(
            top=200, right=400, bottom=2000, left=2200
        )
        self._settings["CLEAR_CROP"]: CropParams = CropParams(
            top=170, right=250, bottom=1350, left=1450
        )
        self._settings["UM_CROP"]: CropParams = CropParams(
            top=0, right=0, bottom=820, left=660
        )
        self._settings["MOON_CROP"]: CropParams = CropParams(
            left=230, top=290, right=1250, bottom=950
        )
        self._settings["MOON_END_DATE_RANGE"]: str = "31/01/2024"
        self._settings["EXEC_CHROME_PATH"]: str = os.path.join(
            self.ROOT_PATH, "chromedriver_win32", "chromedriver.exe"
        )
        self._settings["LOGS_PATH"]: str = os.path.join(self.ROOT_PATH, "logs")
        self._settings["DISCORD_LOGS"]: str = "logs/discord/{date}.log"
        self._settings["DB_CONFIG"]: dict = {
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
        self._settings["CHANNELS"] = {}

        if not os.path.exists(self._settings["MEDIA"]):
            os.mkdir(self._settings["MEDIA"])

        if not os.path.exists(self._settings["LOGS_PATH"]):
            os.mkdir(self._settings["LOGS_PATH"])

        try:
            import _local_settings

            for key in dir(_local_settings):
                if not key.startswith("__") and not key.endswith("__"):
                    self._settings[key] = getattr(_local_settings, key)
        except ImportError:
            pass

        matrix_path: str = self.ROOT_PATH
        if self._settings["BIN_PATH"]:
            matrix_path: str = os.path.join(self.ROOT_PATH, self._settings["BIN_PATH"])

        self._settings["MATRIX_RESHAPE"] = None

        if os.path.isfile(matrix_path):
            matrix = numpy.fromfile(matrix_path)
            self._settings["MATRIX_RESHAPE"] = numpy.reshape(matrix, (616, 448, 2))

    def __getattr__(self, key):
        return self._settings.get(key)

    def set_setting(self, key, value):
        self._settings[key] = value
        if key == "ROOT_PATH":
            self.ROOT_PATH = value

    @property
    def db_config(self):
        return self._settings["DB_CONFIG"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
