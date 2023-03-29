import datetime
import os
import tempfile
from typing import Optional, Union, List, Tuple
from unittest.mock import patch, Mock

import numpy
import pytest
from PIL import Image
from numpy import array
from pytest_mock import MockerFixture

from repos.models import Coords
from repos.repo_types import Coords2Points, UmMeteoGram
from tests.tests_utils import create_images
import use_cases
from use_cases.use_case import DiscordUseCase

from settings import Settings
from utils.utils import URLConfig


def test_discord_use_case_search_index(
    discord_use_case: DiscordUseCase, matrix: array
) -> None:
    """Test searching_index_in_file method"""

    with Settings() as settings:
        settings.MATRIX_RESHAPE = matrix

        res: Coords2Points = discord_use_case.searching_index_in_file(
            54.15, 19.24, matrix
        )

        assert isinstance(res, Coords2Points)
        assert res.act_x == 409
        assert res.act_y == 80

        res = discord_use_case.searching_index_in_file(5.95, 19.24, matrix)

        assert isinstance(res, Coords2Points)
        assert res.act_x == 52
        assert res.act_y == 31


def test_merging_two_photos(
    discord_use_case: DiscordUseCase, mocker: "MockerFixture"
) -> None:
    """Testing merging_two_photos method"""

    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("urllib.request.urlretrieve", return_value="")

    with tempfile.TemporaryDirectory() as tmp_dir:
        images: UmMeteoGram = create_images(tmp_dir)

        root_path: str = images.base_img.url.split("utils")[0]

        discord_use_case.settings.set_setting("ROOT_PATH", root_path)
        discord_use_case.settings.set_setting("MEDIA", root_path)

        res: str = discord_use_case.merging_two_photos(" ")

        assert res

        img: Image = Image.open(res)
        expected_size = (
            images.base_img.size[0] + images.extra_img.size[0],
            images.base_img.size[1],
        )

        assert img.size == expected_size

        img.close()
        images.base_img.close()
        images.extra_img.close()


@pytest.mark.asyncio
async def test_icm_database_search_no_bin_file(
    discord_use_case: DiscordUseCase, mocker: "MockerFixture"
) -> None:
    """Test icm_database_search method with no bin file, no Coords, no URL"""

    with Settings() as settings:
        settings.MATRIX_RESHAPE = None
        mocker.patch("repos.api_repo.APIRepo.get_icm_result", return_value=None)

        res: Optional[str] = await discord_use_case.icm_database_search(
            city="City", coords=None
        )

        assert not res


@pytest.mark.asyncio
async def test_icm_database_search_no_url_no_cords(
    discord_use_case: DiscordUseCase, mocker: "MockerFixture", matrix: numpy.ndarray
) -> None:
    """Test main method for generating image url. No url, bin file served. No Coords"""

    with Settings() as settings:
        settings.MATRIX_RESHAPE = matrix

        mocker.patch("repos.api_repo.APIRepo.get_icm_result", return_value=None)

        res: Optional[str] = await discord_use_case.icm_database_search(
            city="City", coords=None
        )

        assert not res


@pytest.mark.asyncio
async def test_icm_database_search_url(
    discord_use_case: DiscordUseCase, mocker: "MockerFixture", matrix: numpy.ndarray
) -> None:
    """Test main method for generating image url. URL returned"""

    with Settings() as settings:
        settings.MATRIX_RESHAPE = matrix

        with tempfile.TemporaryDirectory() as tmp_dir:
            images: UmMeteoGram = create_images(tmp_dir)

        expected: str = URLConfig.MGRAM_URL.format(act_y="100", act_x="200", uuid="3")

        mocker.patch("repos.api_repo.APIRepo.get_icm_result", return_value=expected)
        mocker.patch(
            "use_cases.use_case.DiscordUseCase.merging_two_photos",
            return_value=images.base_img.url,
        )

        res: Optional[str] = await discord_use_case.icm_database_search(
            city="City", coords=None
        )

        assert res
        assert res == images.base_img.url


@pytest.mark.asyncio
async def test_icm_database_search_no_url_but_bin_file(
    discord_use_case: DiscordUseCase, mocker: "MockerFixture", matrix: numpy.ndarray
) -> None:
    """Test main method for generating image url. URL not returned"""

    discord_use_case.settings.set_setting("MATRIX_RESHAPE", matrix)
    with tempfile.TemporaryDirectory() as tmp_dir:
        images: UmMeteoGram = create_images(tmp_dir)

    mocker.patch("repos.api_repo.APIRepo.get_icm_result", return_value=None)
    mocker.patch(
        "use_cases.use_case.DiscordUseCase.merging_two_photos",
        return_value=images.base_img.url,
    )

    index_result: Coords2Points = Coords2Points(act_x=409, act_y=80)
    mocker.patch(
        "use_cases.use_case.DiscordUseCase.searching_index_in_file",
        return_value=index_result,
    )

    expected: str = URLConfig.MGRAM_URL.format(act_y="100", act_x="200", uuid="3")
    mocker.patch("repos.api_repo.APIRepo.prepare_metagram_url", return_value=expected)

    res: Optional[str] = await discord_use_case.icm_database_search(
        city="City", coords=Coords(latitude=54.25, longitude=35.35)
    )

    assert res
    assert res == images.base_img.url


@pytest.mark.asyncio
async def test_get_moon_img(
    discord_use_case: DiscordUseCase, mocker: "MockerFixture"
) -> None:
    """Test merging_two_photos method. Valid data"""

    class ImageClassExample:
        def __init__(self, url):
            self.url: Optional[str] = url

    class MoonModelTest:
        def __init__(self, date: datetime, image: str):
            self.date = date
            self.image = ImageClassExample(url=image)

    obj: MoonModelTest = MoonModelTest(
        date=datetime.datetime.now(), image="example.jpg"
    )
    db_res: List[MoonModelTest] = [obj]

    mocker.patch("repos.db_repo.MoonRepo.filter", return_value=db_res)

    res: Union[str, dict] = await discord_use_case.get_moon_img("20.02.2023")
    assert res
    assert isinstance(res, str)
    assert res == obj.image.url


@pytest.mark.asyncio
async def test_get_moon_img_day_is_wrong(discord_use_case: DiscordUseCase):
    """Test merging_two_photos method. Wrong day sent"""

    res: Union[str, dict] = await discord_use_case.get_moon_img("35.02.2023")
    assert res
    assert isinstance(res, dict)
    assert res.get("error") == "Day or month is out of range"


@pytest.mark.asyncio
async def test_get_moon_img_empty_res(
    discord_use_case: DiscordUseCase, mocker: "MockerFixture"
):
    """Test merging_two_photos method. No DB query"""

    mocker.patch("repos.db_repo.MoonRepo.filter", return_value=[])

    res: Union[str, dict] = await discord_use_case.get_moon_img("20.02.2023")
    assert res
    assert isinstance(res, dict)
    assert res.get("error") == f"No moon data available for day 20.02.2023"


@pytest.mark.asyncio
async def test_get_sat_url(discord_use_case: DiscordUseCase, mocker: "MockerFixture"):
    """Test get_sat_url method"""
    sunset: datetime = datetime.datetime.now()
    new_sunset: datetime = sunset.replace(hour=23)

    sunrise: datetime = datetime.datetime.now()
    new_sunrise: datetime = sunrise.replace(hour=5)

    expected_sunrise_sunset: Tuple[datetime, datetime] = new_sunrise, new_sunset

    now: datetime = datetime.datetime.now()
    new_now: datetime = now.replace(hour=23, minute=20)
    datetime_mock = Mock(wraps=datetime.datetime)
    datetime_mock.now.return_value = new_now

    mocked_datetime = mocker.patch(
        "use_cases.use_case.dt",
    )
    mocked_datetime.datetime.now.return_value = new_now

    # with patch('datetime.datetime', new=datetime_mock) as mock_datetime:
        # mock_datetime.now.return_value = new_now
    mocker.patch(
        "repos.api_repo.APIRepo.get_sunrise_time",
        return_value=expected_sunrise_sunset,
    )
    settings: Settings = Settings()
    expected_result = os.path.join(settings.MEDIA, "infra_sat.gif")
    res: Union[str, dict] = await discord_use_case.get_sat_url()

    assert res
    assert isinstance(res, str)
    assert expected_result == res
