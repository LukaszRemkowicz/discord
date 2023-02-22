import numpy as np
import pytest
from numpy import ndarray

from repos.api_repo import APIRepo
from repos.db_repo import MoonRepo
from use_cases.use_case import DiscordUseCase


@pytest.fixture
def discord_use_case():
    return DiscordUseCase(
        db_repo=MoonRepo,
        scrapper_repo=APIRepo,
    )


@pytest.fixture
def matrix() -> ndarray:
    arr: ndarray = np.array([el * 0.0005 for el in range(0, 551936)])
    new_arr: ndarray = np.reshape(arr, (616, 448, 2))
    return new_arr


@pytest.fixture
def city_result_template():
    with open("tests/fixtures/template/search_res.html", "r", encoding='iso-8859-2') as f:
        file = f.read()
    return file


@pytest.fixture
def city_result_template_no_res():
    with open("tests/fixtures/template/search_res_no_res.html", "r", encoding='iso-8859-2') as f:
        file = f.read()
    return file


@pytest.fixture
def city_response():
    with open("tests/fixtures/template/response.html", "r", encoding='iso-8859-2') as f:
        file = f.read()
    return file
