import re
import uuid
from typing import Optional, List

import bs4
import requests
from geopy import Nominatim, Location
from requests import Response

from logger import ColoredLogger, get_module_logger
from repos.consts import headers
from repos.models import Coords
from repos.types import Coords2Points
from utils.utils import URLConfig

logger: ColoredLogger = get_module_logger("APIRepo")


class APIRepo:
    """Base repo responsible for handling requests"""

    def __init__(self) -> None:
        self.urls: URLConfig = URLConfig()
        self.session: requests.Session = requests.Session()
        self.headers: dict = headers

    async def __fetch_data_post(self, url: str, **kwargs) -> Response:
        self.session.headers.update(self.headers)
        logger.info(f"Started parsing {url}")
        response: Response = self.session.post(url=url, **kwargs)
        response.raise_for_status()
        logger.info("Success")
        return response

    async def __fetch_data_get(self, url: str) -> Response:
        self.session.headers.update(self.headers)
        logger.info(f"Started parsing {url}")
        response: Response = self.session.get(url=url)
        response.raise_for_status()
        logger.info("Success")
        return response

    @staticmethod
    async def get_coords(city: str) -> Optional[Coords]:
        geolocator: Nominatim = Nominatim(user_agent="lukas")
        location: Location = geolocator.geocode(city)

        if not location:
            return None

        return Coords(latitude=location.latitude, longitude=location.longitude)

    async def get_icm_result(self, **kwargs) -> Optional[str]:
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
        return self.urls.MGRAM_URL.format(
            act_y=coords2points.act_y, act_x=coords2points.act_x, uuid=str(uuid.uuid1())
        )
