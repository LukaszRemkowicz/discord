import os
import urllib.request
from datetime import datetime, timedelta
from typing import Union, Optional, Type, List

import numpy
from PIL import Image
from numpy import ndarray

from logger import ColoredLogger, get_module_logger
from repos.api_repo import APIRepo
from repos.db_repo import MoonRepo
from repos.models import Coords, MoonModel
from repos.types import Coords2Points
from settings import Settings

# settings: Settings = Settings()

logger: ColoredLogger = get_module_logger("USE_CASE")


class DiscordUseCase:
    def __init__(
        self,
        db_repo: Union[Type[MoonRepo]] = MoonRepo,
        scrapper_repo: Union[Type[APIRepo]] = APIRepo,
    ):
        self.db: MoonRepo = db_repo()
        self.scrapper: APIRepo = scrapper_repo()
        self.settings = Settings()

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

        utils_base_photo: str = os.path.join("utils", "base.png")
        base_photo: str = os.path.join(self.settings.ROOT_PATH, utils_base_photo)

        if not os.path.exists(base_photo):
            urllib.request.urlretrieve(
                self.settings.METEO_BASE_PHOTO_URL, utils_base_photo
            )

        save_name: str = os.path.join(self.settings.ROOT_PATH, "my_image.png")
        urllib.request.urlretrieve(url, save_name)
        logger.info(f"Parsing url: {url}")

        image1: Image = Image.open(os.path.join(self.settings.ROOT_PATH, base_photo))
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
        new_path: str = os.path.join(self.settings.MEDIA, "merged_image.jpg")
        new_image.save(new_path, "png")

        os.remove(save_name)

        return new_path

    async def icm_database_search(
        self, city: str, coords: Optional[Coords]
    ) -> Optional[str]:
        """Search city points. Firstly trying to get it from meteo "API", later from bin file"""
        url: str = await self.scrapper.get_icm_result(data={"name": city})
        logger.info(f"Method icm_database_search, url: {url}")

        if not url and not self.settings.MATRIX_RESHAPE.any():
            return

        if not url and not coords:
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
            date_obj: datetime = datetime(int(year), int(month), int(day), 0, 0, 0)
        except ValueError as err:
            logger.error(err)
            return {"error": "Day or month is out of range"}
        res: List[MoonModel] = await self.db.filter(
            date__gte=date_obj, date__lt=date_obj + timedelta(days=1)
        )

        if res:
            return res[0].image.url
        return {"error": f"No moon data available for day {date_str}"}
