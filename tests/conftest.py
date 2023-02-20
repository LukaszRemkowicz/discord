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
