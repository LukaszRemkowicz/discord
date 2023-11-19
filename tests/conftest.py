import asyncio
import warnings
from typing import Iterator
from unittest import mock

import numpy as np
import pytest
import requests
from numpy import ndarray
from tortoise.contrib.test import finalizer, initializer

from repos.api_repo import APIRepo
from repos.db_repo import MoonRepo
from settings import settings
from use_cases.use_case import DiscordUseCase


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    """Disable network calls during tests"""

    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())


@pytest.fixture
def discord_use_case() -> DiscordUseCase:
    """Return DiscordUseCase instance"""
    return DiscordUseCase(
        db_repo=MoonRepo,
        scrapper_repo=APIRepo,
    )


@pytest.fixture
def matrix() -> ndarray:
    """Return ndarray with shape (616, 448, 2)"""
    arr: ndarray = np.array([el * 0.0005 for el in range(0, 551936)])
    new_arr: ndarray = np.reshape(arr, (616, 448, 2))
    return new_arr


@pytest.fixture
def city_result_template() -> str:
    """Return html template with search results"""
    with open(
        "tests/fixtures/template/search_res.html", "r", encoding="iso-8859-2"
    ) as f:
        file = f.read()
    return file


@pytest.fixture
def city_result_template_no_res() -> str:
    """Return html template with no search results"""
    with open(
        "tests/fixtures/template/search_res_no_res.html", "r", encoding="iso-8859-2"
    ) as f:
        file = f.read()
    return file


@pytest.fixture
def city_response() -> str:
    """Return html template with city response"""
    with open("tests/fixtures/template/response.html", "r", encoding="iso-8859-2") as f:
        file = f.read()
    return file


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def ignore_warnings():
    """Ignore warnings during tests."""
    # FIXME: find a way to solve this warning
    warnings.filterwarnings("ignore", message='Module "__main__" has no models')


@pytest.fixture(scope="session", autouse=True)
def db_initializer(request, event_loop):
    """Initialize test database."""
    # TODO: think about creating separate test database credentials in env file or in settings
    credentials: dict = {
        "host": settings.db.HOST,
        "port": settings.db.PORT,
        "user": settings.db.USERNAME,
        "password": settings.db.PASSWORD.get_secret_value(),
        "database": "discord_test_db",
    }
    user_credentials = f"{credentials['user']}:{credentials['password']}"
    db_host = f"127.0.0.1:{credentials['port']}/{credentials['database']}"
    initializer(
        db_url=f"postgres://{user_credentials}@{db_host}",
        modules=["repos.models"],
        loop=event_loop,
    )
    patcher = mock.patch(
        "settings.DatabaseSettings.credentials", return_value=credentials
    )
    patcher.start()

    request.addfinalizer(finalizer)
