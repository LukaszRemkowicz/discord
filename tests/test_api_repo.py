import pytest
import requests_mock

from repos.api_repo import APIRepo


@pytest.mark.asyncio
async def test_api_repo_fetch_data() -> None:
    """Test if main method is working fine"""
    content: dict = {"data": {"name": "city_name"}}
    with requests_mock.Mocker() as mock_request:
        mock_request.post("https://example_url", json=content)
        response = await APIRepo()._APIRepo__fetch_data_post("https://example_url", **content)  # type: ignore
    assert response.json() == content


@pytest.mark.asyncio
async def test_api_repo_fetch_data(city_result_template, city_response) -> None:
    api_repo = APIRepo()
    api_repo.urls.UM_URL = "https://example_url_one"
    api_repo.urls.METEOGRAM_URL = "https://example_url_two"

    content: dict = {"data": {"name": "city_name"}}

    with requests_mock.Mocker() as mock_request:
        mock_request.post(api_repo.urls.UM_URL, text=city_result_template)
        mock_request.get(api_repo.urls.METEOGRAM_URL, text=city_response)

        result = await api_repo.get_icm_result(**content)

        assert api_repo.urls.MGRAM_URL.split("?")[0] in result
        assert "row=352" in result
        assert "col=222" in result


@pytest.mark.asyncio
async def test_api_repo_fetch_data_no_result(city_result_template_no_res, city_response) -> None:
    api_repo = APIRepo()
    api_repo.urls.UM_URL = "https://example_url_one"

    content: dict = {"data": {"name": "city_name"}}

    with requests_mock.Mocker() as mock_request:
        mock_request.post(api_repo.urls.UM_URL, text=city_result_template_no_res)
        result = await api_repo.get_icm_result(**content)

        assert not result
