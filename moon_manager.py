import asyncio
import os
import time
from datetime import datetime
from typing import Tuple, Optional, Union

from PIL import Image
from selenium.common import WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver

from logger import ColoredLogger, get_module_logger
from repos.repo_types import CropParams
from settings import Settings
from utils.utils import start_driver, daterange  # type: ignore
from repos.models import MoonModel
from utils.db_utils import DBConnectionHandler

settings: Settings = Settings()

logger: ColoredLogger = get_module_logger("MOON")


class MoonManager:
    def __init__(self, driver: Union[WebDriver], day: bool = False):
        self.folder_name: str = f"{settings.ROOT_PATH}/moon/"
        self.driver = driver
        # self.base_url: str = "http://www.lowiecki.pl/ao/w/{year}/{month}.htm"
        self.base_url: str = "https://fazyksiezyca24.pl/{year}/{month}/{day}"
        self.xpath: str = "/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/button[1]/p"
        self.crop: CropParams = settings.MOON_CROP
        self.date_range_by_day = daterange(
            datetime.date(datetime.now()),
            datetime.date(datetime.strptime(settings.MOON_END_DATE_RANGE, "%d/%m/%Y")),
        )
        self.day = day
        self.db: MoonModel = MoonModel()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    async def create_new_file_path(self) -> str:
        """Create new file path with given filename"""
        name_of_file: str = time.asctime().replace(":", "-")
        file_name: str = os.path.join(self.folder_name, name_of_file + ".png")
        return file_name

    async def take_a_screenshot(self) -> str:
        """Save the file on the hard drive. Returns file path"""
        screenshot_path: str = await self.create_new_file_path()
        self.driver.save_screenshot(screenshot_path)
        return screenshot_path

    async def crop_file(
        self, file: Image, year: int, month: int, day: Optional[int] = None
    ) -> str:
        """Crop file and return new path. Example path: {ROOT_PATH}/moon/2023-02-22.png"""

        image_crop = file.crop(
            (self.crop.left, self.crop.top, self.crop.right, self.crop.bottom)
        )
        day2str: Union[int, str] = day
        if day:
            day2str = str(day) if len(str(day)) == 2 else f"0{str(day)}"

        month2str: str = str(month) if len(str(month)) == 2 else f"0{str(month)}"
        file_name: str = os.path.join(
            self.folder_name, f"{str(year)}-{month2str}-{day2str}.png"
        )

        if os.path.exists(file_name):
            return file_name

        image_crop.save(file_name, quality=95)
        return file_name

    async def prepare_moon_photos(self) -> None:
        """Main class method."""
        if self.day:
            await self.loop_by_days()
        await self.loop_by_months()

    async def loop_by_months(self):
        for day in self.date_range_by_day:
            url: str = self.base_url.format(year=day.year, month=day.month)
            logger.info(f"Parsing url {url}")
            file_path, file = self.get_file(url)
            await self.crop_file(file=file, year=day.year, month=day.month)
            os.remove(file_path)

    async def loop_by_days(self) -> None:
        async with DBConnectionHandler():
            for day in self.date_range_by_day:
                url: str = self.base_url.format(
                    year=day.year, month=day.month, day=day.day
                )
                logger.info(f"Parsing url {url}")
                file_path, file = await self.get_file(url)
                crop_file_path: str = await self.crop_file(
                    file=file, year=day.year, month=day.month, day=day.day
                )
                await self.db.create(
                    date=day.strftime("%Y-%m-%d"), image=crop_file_path
                )
                logger.info("Saved pic to DB")
                os.remove(file_path)

    async def get_file(self, url) -> Tuple[str, Image.Image]:
        self.driver.get(url)
        time.sleep(0.5)

        try:
            self.driver.find_element("xpath", self.xpath).click()
        except WebDriverException:
            pass  # Do not raise exception

        file_name: str = await self.take_a_screenshot()
        file: Image = Image.open(file_name)
        return file_name, file


def run_moon_script():
    async def main():
        async with MoonManager(driver=start_driver(), day=True) as moon:
            await moon.prepare_moon_photos()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


run_moon_script()
