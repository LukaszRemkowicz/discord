import os
import urllib.request
from datetime import datetime, timedelta
from typing import Union, Optional, Type

import numpy
from PIL import Image
from numpy import ndarray

from logger import ColoredLogger, get_module_logger
from repos.api_repo import APIRepo
from repos.db_repo import MoonRepo
from repos.models import Coords
from repos.types import Coords2Points
from settings import MATRIX_RESHAPE, METEO_BASE_PHOTO_URL, MEDIA

logger: ColoredLogger = get_module_logger("USE_CASE")


class DiscordUseCase:
    def __init__(self, db_repo: Union[Type[MoonRepo]] = MoonRepo, scrapper_repo: Union[Type[APIRepo]] = APIRepo):
        self.db: MoonRepo = db_repo()
        self.scrapper: APIRepo = scrapper_repo()

    async def get_coords(self, city: str) -> Optional[Coords]:
        coords: Union[Coords] = await self.scrapper.get_coords(city)
        if coords:
            return coords

    @staticmethod
    def searching_index_in_file(
            long: float, lat: float, array: ndarray
    ) -> Coords2Points:
        """Search city points in meteo grid (.bin file)"""

        longitude_arr: ndarray = array[:, :, 1] - long
        latitude_arr: ndarray = array[:, :, 0] - lat
        distance_between_points: ndarray = numpy.sqrt(
            longitude_arr ** 2 + latitude_arr ** 2
        )
        array_with_distance_results: tuple = numpy.unravel_index(
            numpy.argmin(distance_between_points), distance_between_points.shape
        )
        # new_coords = (
        #     10 + round((array_with_distance_results[0] - 10) / 7) * 7,
        #     10 + round((array_with_distance_results[1] - 10) / 7) * 7,
        # )
        return Coords2Points(
            act_x=10 + round((array_with_distance_results[1] - 10) / 7) * 7,
            act_y=10 + round((array_with_distance_results[0] - 10) / 7) * 7,
        )

    @staticmethod
    def merging_two_photos(url) -> str:
        """Merge two meteo photos. Base img and meteogram"""

        base_photo: str = "base.png"
        urllib.request.urlretrieve(METEO_BASE_PHOTO_URL, base_photo)
        save_name: str = "my_image.png"
        urllib.request.urlretrieve(url, save_name)
        image1: Image = Image.open(base_photo)
        image2: Image = Image.open(save_name)

        image1_width: int
        image1_height: int
        image2_width: int
        image2_height: int

        image1_width, image1_height = image1.size
        image2_width, image2_height = image2.size

        new_image: Image = Image.new(
            "RGB", (image1_width + image2_width, image1_height)
        )
        new_image.paste(image1, (0, 0))
        new_image.paste(image2, (image1_width, 0))
        new_path: str = os.path.join(MEDIA, "merged_image.jpg")
        new_image.save(new_path, "png")
        return new_path

    async def icm_database_search(self, city: str, coords: Coords) -> Optional[str]:
        """Search city points. Firstly trying to get it from meteo "API", later from bin file"""
        url: str = await self.scrapper.get_icm_result(data={"city": city})

        if not url:
            coords2points: Coords2Points = self.searching_index_in_file(
                coords.latitude, coords.longitude, MATRIX_RESHAPE
            )
            url: str = self.scrapper.prepare_metagram_url(coords2points)
        path_of_new_file: str = self.merging_two_photos(url=url)
        return path_of_new_file

    async def get_moon_img(self, date_str: str):
        day, month, year = date_str.split('.')
        try:
            date_obj: datetime = datetime(int(year), int(month), int(day), 0, 0, 0)
        except ValueError as err:
            logger.error(err)
            return {"error": f"Day or month is out of range"}
        res = await self.db.filter(date__gte=date_obj, date__lt=date_obj + timedelta(days=1))
        breakpoint()
        if res:
            return res[0].image.url
        return {"error": f"No moon data available for day {date_str}"}
