from datetime import timedelta, datetime
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from settings import Settings

settings: Settings = Settings()


class URLConfig:
    UM_URL = "https://www.meteo.pl/um/php/gpp/next.php"
    METEOGRAM_URL = (
        "http://www.meteo.pl/um/php/meteorogram_id_um.php?ntype=0u&id={id}"  # noqa
    )
    MGRAM_URL = "http://www.meteo.pl/um/metco/mgram_pict.php?ntype=0u&row={act_y}&col={act_x}&lang=pl&uid={uuid}"  # noqa


def start_driver():
    chrome_options = Options()
    for option in settings.CHROME_DRIVER_OPTIONS:
        chrome_options.add_argument(option)

    return webdriver.Chrome(settings.EXEC_CHROME_PATH, options=chrome_options)


def daterange(start_date: datetime.date, end_date: datetime.date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


class Validator:
    def __init__(self, date: Optional[str] = None, city: Optional[str] = None):
        self.date = date
        self.city = city

    def __enter__(self):
        if self.date and len(self.date.split(".")) < 3:
            return {"error": "Date is not valid. Should be format like: '20.01.2023'"}

        return self.date

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
