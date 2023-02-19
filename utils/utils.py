from datetime import timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from settings import CHROME_DRIVER_OPTIONS, EXEC_CHROME_PATH


class URLConfig:
    UM_URL = "https://www.meteo.pl/um/php/gpp/next.php"
    METEOGRAM_URL = "http://www.meteo.pl/um/php/meteorogram_id_um.php?ntype=0u&id={id}"  # noqa
    MGRAM_URL = "http://www.meteo.pl/um/metco/mgram_pict.php?ntype=0u&row={act_y}&col={act_x}&lang=pl&uid={uuid}"  # noqa


def start_driver():
    chrome_options = Options()
    for option in CHROME_DRIVER_OPTIONS:
        chrome_options.add_argument(option)

    return webdriver.Chrome(EXEC_CHROME_PATH, options=chrome_options)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)
