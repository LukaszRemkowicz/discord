import tempfile

from PIL import Image
from numpy import array
from pytest_mock import MockerFixture

from repos.types import Coords2Points, UmMeteoGram
from tests.tests_utils import create_images
from use_cases.use_case import DiscordUseCase

from settings import Settings


def test_discord_use_case_search_index(
    discord_use_case: DiscordUseCase, matrix: array
):
    """Test searching_index_in_file method"""
    with Settings() as settings:
        settings.MATRIX_RESHAPE = matrix

        res = discord_use_case.searching_index_in_file(54.15, 19.24, matrix)

        assert isinstance(res, Coords2Points)
        assert res.act_x == 409
        assert res.act_y == 80

        res = discord_use_case.searching_index_in_file(5.95, 19.24, matrix)

        assert isinstance(res, Coords2Points)
        assert res.act_x == 52
        assert res.act_y == 31


def test_merging_two_photos(
    discord_use_case: DiscordUseCase, mocker: "MockerFixture"
):
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("urllib.request.urlretrieve", return_value="")

    with tempfile.TemporaryDirectory() as tmp_dir:
        images: UmMeteoGram = create_images(tmp_dir)

        root_path = images.base_img.url.split("utils")[0]

        discord_use_case.settings.set_setting("ROOT_PATH", root_path)
        discord_use_case.settings.set_setting("MEDIA", root_path)

        res = discord_use_case.merging_two_photos(" ")

        assert res

        img = Image.open(res)
        expected_size = (images.base_img.size[0] + images.extra_img.size[0], images.base_img.size[1])

        assert img.size == expected_size

        img.close()
        images.base_img.close()
        images.extra_img.close()
