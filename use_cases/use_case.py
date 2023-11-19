import os
from datetime import datetime as dt
from datetime import timedelta
from pathlib import Path
from types import GeneratorType
from typing import List, Optional, Type, Union

import numpy
from numpy import ndarray
from PIL import Image

from logger import ColoredLogger, get_module_logger
from repos.api_repo import APIRepo, UrlLibRequest
from repos.db_repo import MoonRepo
from repos.models import Coords, MoonModel
from repos.repo_types import Coords2Points
from settings import settings
from use_cases.managers import UMPhotoManager
from utils.utils import daterange_by_minutes

logger: ColoredLogger = get_module_logger("USE_CASE")


class DiscordUseCase:
    def __init__(
        self,
        db_repo: Union[Type[MoonRepo]] = MoonRepo,
        scrapper_repo: Union[Type[APIRepo]] = APIRepo,
    ):
        self.db: MoonRepo = db_repo()
        self.scrapper: APIRepo = scrapper_repo()
        self.settings = settings

    async def get_coords(self, city: str) -> Optional[Coords]:
        coords: Union[Coords] = await self.scrapper.get_coords(city)
        if coords:
            logger.info(
                f"Method get_coords, coords found: {coords.latitude, coords.longitude}"
            )
            return coords
        logger.info(f"Method get_coords, coords for city {city}not found")

    @staticmethod
    def searching_index_in_file(
        long: float, lat: float, array: ndarray
    ) -> Coords2Points:
        """Search city points in meteo grid (.bin file)"""

        longitude_arr: ndarray = array[:, :, 1] - long
        latitude_arr: ndarray = array[:, :, 0] - lat
        distance_between_points: ndarray = numpy.sqrt(
            longitude_arr**2 + latitude_arr**2
        )
        array_with_distance_results: tuple = numpy.unravel_index(
            numpy.argmin(distance_between_points), distance_between_points.shape
        )
        # new_coords = (
        #     10 + round((array_with_distance_results[0] - 10) / 7) * 7,
        #     10 + round((array_with_distance_results[1] - 10) / 7) * 7,
        # )
        act_x: int = 10 + round((array_with_distance_results[1] - 10) / 7) * 7
        act_y: int = 10 + round((array_with_distance_results[0] - 10) / 7) * 7
        logger.info(
            f"Method: searching_index_in_file, points from file found: {act_x, act_y}"
        )

        return Coords2Points(act_x=act_x, act_y=act_y)

    def merging_two_photos(self, url) -> str:
        """Merge two meteo photos. Base img and meteogram"""

        base_photo: str = os.path.join(self.settings.ROOT_PATH, settings.um.BASE_PHOTO)

        if not os.path.exists(base_photo):
            UrlLibRequest().get_base_image(
                self.settings.METEO_BASE_PHOTO_URL, settings.um.BASE_PHOTO
            )

        temporary_file_path: Path = (
            Path(self.settings.ROOT_PATH) / settings.temp_file_name
        )
        UrlLibRequest().get_base_image(url, temporary_file_path)

        image1: Image = Image.open(os.path.join(self.settings.ROOT_PATH, base_photo))
        image2: Image = Image.open(temporary_file_path)

        new_path: str = UMPhotoManager.merge_photos(image1, image2)
        os.remove(temporary_file_path)

        return new_path

    async def icm_database_search(
        self, city: str, coords: Optional[Coords]
    ) -> Optional[str]:
        """Search city points. Firstly trying to get it from meteo "API", later from bin file"""
        url: str = await self.scrapper.get_icm_result(data={"name": city})
        logger.info(f"Method icm_database_search, url: {url}")

        if not url and not isinstance(self.settings.MATRIX_RESHAPE, numpy.ndarray):
            logger.info(f"Matrix is None. Cannot obtain city {city} data")
            return

        if not url and not coords:
            logger.info(f"Url and coords are None. Cannot obtain city {city} data")
            return

        if not url:
            coords2points: Coords2Points = self.searching_index_in_file(
                coords.latitude, coords.longitude, self.settings.MATRIX_RESHAPE
            )
            url: str = self.scrapper.prepare_metagram_url(coords2points)
            logger.info(f"Url not found, preparing from file: {url}")

        path_of_new_file: str = self.merging_two_photos(url=url)
        return path_of_new_file

    async def get_moon_img(self, date_str: str) -> Union[str, dict]:
        day, month, year = date_str.split(".")
        try:
            date_obj: dt = dt(int(year), int(month), int(day), 0, 0, 0)
        except ValueError as err:
            logger.error(err)
            return {"error": "Day or month is out of range"}

        res: List[MoonModel] = await self.db.filter(
            date__gte=date_obj, date__lt=date_obj + timedelta(days=1)
        )

        if res:
            return res[0].image.url
        return {"error": f"No moon data available for day {date_str}"}

    async def get_sat_url(self):
        sunrise, sunset = await self.scrapper.get_sunrise_time()
        date_now: dt = dt.now()
        generator: GeneratorType = daterange_by_minutes(sunrise, sunset)
        if date_now.strftime("%Y-%m-%d %H:%M") in generator:
            return await UrlLibRequest().get_sat_img()
        return await UrlLibRequest().get_sat_infra_img()
