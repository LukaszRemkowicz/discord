import json
import re
import urllib
import uuid
from datetime import datetime as dt
from http.client import HTTPMessage
from pathlib import Path
from typing import List, Optional, Tuple, Type
from urllib import request

import bs4
import requests
from geopy import Location, Nominatim
from geopy.exc import GeocoderUnavailable
from requests import Response

from logger import ColoredLogger, get_module_logger
from repos.consts import HEADERS
from repos.models import Coords
from repos.repo_types import Coords2Points, RequestHeaders, RequestHeadersProtocol
from settings import settings
from utils.utils import URLConfig

logger: ColoredLogger = get_module_logger("APIRepo")


class APIRepo:
    """Base repo responsible for handling requests"""

    def __init__(self) -> None:
        self.urls: URLConfig = URLConfig()
        self.session: requests.Session = requests.Session()
        self.headers: dict = HEADERS

    async def __fetch_data_post(self, url: str, **kwargs) -> Response:
        """Private method for fetching data from given url. POST method"""
        self.session.headers.update(self.headers)
        logger.info(f"Started parsing {url}")
        response: Response = self.session.post(url=url, **kwargs)
        response.raise_for_status()
        logger.info("Success")
        return response

    async def __fetch_data_get(self, url: str, headers: bool = True) -> Response:
        """Private method for fetching data from given url. GET method"""
        if headers:
            self.session.headers.update(self.headers)
        logger.info(f"Started parsing {url}")
        response: Response = self.session.get(url=url)
        response.raise_for_status()
        logger.info("Success")
        return response

    @staticmethod
    async def get_coords(city: str) -> Optional[Coords]:
        """Get coords from given city name."""
        geolocator: Nominatim = Nominatim(user_agent="lukas")
        try:
            location: Location = geolocator.geocode(city)
        except GeocoderUnavailable:
            location: None = None

        if not location:
            return None

        return Coords(latitude=location.latitude, longitude=location.longitude)

    async def get_icm_result(self, **kwargs) -> Optional[str]:
        """
        Get icm result from icm database. Flow:
        1. Get html from https://www.meteo.pl/um/php/gpp/next.php passing city name in kwargs
        2. Parse html and get ids from href
        3. Get meteogram url from https://www.meteo.pl/um/php/meteorogram_id_um.php?ntype=0u&id={id} passing id from step 2
        4. Get meteogram from url from step 3
        5. Get act_x and act_y variables from meteogram
        6. Return meteogram url from http://www.meteo.pl/um/metco/mgram_pict.php?ntype=0u&row={act_y}&col={act_x}&lang=pl&uid={uuid}
        """  # noqa: E501
        response: Response = await self.__fetch_data_post(
            self.urls.UM_URL, headers=self.headers, **kwargs
        )
        parse_response: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "lxml")
        if "NIE ZNALEZIONO" in parse_response.text:
            return None

        hrefs: list = list(parse_response.find_all(href=True))
        id_result: list = [
            re.findall("[0-9]+", str(element))  # noqa
            for element in hrefs
            if "show_mgram" in str(element)
        ][0]

        url: str = self.urls.METEOGRAM_URL.format(id=str(id_result[0]))
        get_req: Response = await self.__fetch_data_get(url)

        get_soup: bs4.BeautifulSoup = bs4.BeautifulSoup(get_req.text, "lxml")
        get_scripts: list = get_soup.find_all(language=True)
        scripts: List[str] = str(get_scripts).split(";")
        var_act_x: list = [
            re.findall("[0-9]+", act_x)
            for act_x in scripts
            if "var act_x" in act_x  # noqa
        ]
        var_act_y: list = [
            re.findall("[0-9]+", act_y)
            for act_y in scripts
            if "var act_y" in act_y  # noqa
        ]
        coords2points: Coords2Points = Coords2Points(
            act_x=int(var_act_x[0][0]), act_y=int(var_act_y[0][0])
        )

        if coords2points:
            return self.prepare_metagram_url(coords2points=coords2points)

    def prepare_metagram_url(self, coords2points: Coords2Points) -> str:
        """Prepare meteogram url."""
        return self.urls.MGRAM_URL.format(
            act_y=coords2points.act_y, act_x=coords2points.act_x, uuid=str(uuid.uuid1())
        )

    async def get_sunrise_time(self) -> Tuple[dt, dt]:
        """
        Get sunrise and sunset time from sunrise-sunset.org.
        Method needed for sat24. Sat24 uses map for Poland, so it doesn't matter
        if we get sunrise time for Warsaw or other city. There is not need to extend
        it for other cities.
        """
        coords: Coords = await self.get_coords("Warszawa")
        res: Response = await self.__fetch_data_get(
            self.urls.API_SUNRISE_URL.format(lat=coords.latitude, long=coords.longitude),
            headers=False,
        )

        response_json: dict = json.loads(res.text)
        time_formatter: str = "%Y-%m-%dT%H:%M:%S%z"

        sunrise: dt = dt.strptime(
            response_json.get("results").get("sunrise"), time_formatter
        )
        sunset: dt = dt.strptime(
            response_json.get("results").get("sunset"), time_formatter
        )

        return sunrise, sunset


class UrlLibRequest:
    """UrlLib request handler"""

    def __init__(
        self,
        urls: URLConfig = URLConfig(),
        request_header: Type[RequestHeadersProtocol] = RequestHeaders(),
    ):
        self.urls: URLConfig = urls
        self.headers: RequestHeadersProtocol = request_header

    @staticmethod
    def urlretrieve(url: str, path: Path) -> tuple[str, HTTPMessage]:
        """Download file from given url and save it in given path"""
        logger.info(f"Started downloading file: {url}")
        return urllib.request.urlretrieve(url, path)

    async def get_sat_url(self, url: str, file_name: str) -> str:
        """Download file from given url and save it in given path"""
        file_path: Path = Path(settings.MEDIA) / file_name
        opener = urllib.request.build_opener()
        opener.addheaders = self.headers.to_list(key="User-Agent")
        urllib.request.install_opener(opener)
        self.urlretrieve(url, file_path)
        return str(file_path)

    async def get_sat_img(self) -> str:
        """Get sat image at daylight"""
        return await self.get_sat_url(self.urls.SAT, "sat.gif")

    async def get_sat_infra_img(self) -> str:
        """Get sat image at night (infra)"""
        return await self.get_sat_url(self.urls.SAT_INFRA, "infra_sat.gif")

    def get_base_image(self, url: str, path: Path) -> tuple[str, HTTPMessage]:
        """Download UM base file from given url and save it in given path."""
        return self.urlretrieve(url, path)
