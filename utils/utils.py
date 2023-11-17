import platform
from datetime import timedelta, datetime
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from settings import Settings

settings: Settings = Settings()


class URLConfig:
    UM_URL = "https://www.meteo.pl/um/php/gpp/next.php"
    METEOGRAM_URL = (
        "http://www.meteo.pl/um/php/meteorogram_id_um.php?ntype=0u&id={id}"  # noqa
    )
    MGRAM_URL = "http://www.meteo.pl/um/metco/mgram_pict.php?ntype=0u&row={act_y}&col={act_x}&lang=pl&uid={uuid}"  # noqa
    API_SUNRISE_URL = (
        "https://api.sunrise-sunset.org/json?lat={lat}&lng={long}&formatted=0"
    )
    # SAT_INFRA = "https://api.sat24.com/animated/PL/infraPolair/3/Central%20European%20Standard'%20width=845%20" \
    #             "height=615"
    # SAT = "http://api.sat24.com/animated/PL/visual/3/Central%20European%20Standard'%20width=845%20height=615"

    SAT_INFRA = (
        "https://api.sat24.com/animated/PL/infraPolair/3/Central%20European%20"
        "Standard%20Time/6689549%20width=845%20height=615"
    )
    SAT = (
        "https://api.sat24.com/animated/PL/visual/3/Central%20European%20"
        "Standard%20Time/8708042%20width=845%20height=615"
    )


def start_driver():
    firefox_options = FirefoxOptions()
    chrome_options = Options()
    firefox_options.binary_location = "/usr/bin/firefox-esr"

    for option in settings.CHROME_DRIVER_OPTIONS:
        chrome_options.add_argument(option)
        firefox_options.add_argument(option)

    if "Linux" in platform.platform():
        return webdriver.Firefox(
            options=firefox_options, executable_path=settings.EXEC_CHROME_PATH
        )

    return webdriver.Chrome(settings.EXEC_CHROME_PATH, options=chrome_options)


def daterange(start_date: datetime.date, end_date: datetime.date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def daterange_by_minutes(start_date: datetime.date, end_date: datetime.date):
    minutes = range(0, int((end_date - start_date).total_seconds() / 60))
    for minute in minutes:
        yield (start_date + timedelta(minutes=minute)).strftime("%Y-%m-%d %H:%M")


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
