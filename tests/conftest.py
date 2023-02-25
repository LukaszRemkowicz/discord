import os

import numpy as np
import pytest
import requests
from numpy import ndarray
from pytest_docker.plugin import Services
from pytest_mock import MockerFixture

from repos.api_repo import APIRepo
from repos.db_repo import MoonRepo
from use_cases.use_case import DiscordUseCase
from settings import Settings

from dotenv import dotenv_values

from utils.exceptions import TestDBWrongCredentialsError

env_path: str = os.path.join(Settings().ROOT_PATH, ".env")
env_values = dict(dotenv_values(env_path))

TEST_DB_PASSWORD = env_values.get("POSTGRES_TEST_PASSWORD")
TEST_DB_USER = env_values.get("POSTGRES_TEST_USER")
TEST_DB_NAME = env_values.get("POSTGRES_TEST_DB_NAME")

pytest_plugins = ["docker_compose"]


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    """Disable network calls during tests"""
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())


@pytest.fixture
def discord_use_case() -> DiscordUseCase:
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
def city_result_template() -> str:
    with open(
        "tests/fixtures/template/search_res.html", "r", encoding="iso-8859-2"
    ) as f:
        file = f.read()
    return file


@pytest.fixture
def city_result_template_no_res() -> str:
    with open(
        "tests/fixtures/template/search_res_no_res.html", "r", encoding="iso-8859-2"
    ) as f:
        file = f.read()
    return file


@pytest.fixture
def city_response() -> str:
    with open("tests/fixtures/template/response.html", "r", encoding="iso-8859-2") as f:
        file = f.read()
    return file


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig) -> str:  # noqa
    docker_path: str = os.path.join(
        Settings().ROOT_PATH, "tests", "docker-compose-test.yml"
    )
    return docker_path


@pytest.fixture(scope="session")
def docker_app(docker_services: "Services", docker_ip: str) -> dict:

    user: str = env_values.get("POSTGRES_TEST_USER")
    password: str = env_values.get("POSTGRES_TEST_PASSWORD")
    db_name: str = env_values.get("POSTGRES_TEST_DB_NAME")

    if not user or not db_name or not password:
        raise TestDBWrongCredentialsError()

    port: int = docker_services.port_for("test_db", 5432) or 5450
    credentials: dict = {
        "host": docker_ip,
        "port": port,
        "user": user,
        "password": password,
        "database": db_name,
    }

    # url = f"https://{docker_ip}:{port}"
    # docker_services.wait_until_responsive(
    #     timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    # )
    return credentials


@pytest.fixture(autouse=True)
def _mock_db_connection(mocker: "MockerFixture", docker_app: dict) -> bool:
    """
    Mocking new db credentials to Settings()
    :param mocker: pytest-mock plugin fixture
    :docker_app: new params. Docker instance credentials.
    :return: True upon successful monkey-patching
    """
    db_config: dict = Settings().db_config
    db_config["connections"]["default"]["credentials"] = docker_app
    mocker.patch("settings.Settings.db_config", db_config)
    mocker.patch("settings.Settings.db_config", db_config)

    return True
