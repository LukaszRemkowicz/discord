import datetime
import os
import tempfile
from typing import List
from unittest.mock import PropertyMock

import pytest
from pytest_mock import MockerFixture
from tortoise.exceptions import IntegrityError

from settings import Settings
from repos.db_repo import MoonRepo
from repos.models import MoonModel
from repos.types import UmMeteoGram
from tests.tests_utils import create_images
from utils.db_utils import DBConnectionHandler

settings: Settings = Settings()


@pytest.mark.asyncio
async def test_db_repo(mocker: "MockerFixture") -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        images: UmMeteoGram = create_images(tmp_dir)

        mocker.patch(
            "repos.schemas.FileField.upload_to",
            return_value=os.path.join(images.base_img.root_path, "moon"),
            new_callable=PropertyMock
        )
        os.makedirs(os.path.join(images.base_img.root_path, "moon"))

        async with DBConnectionHandler():
            date: datetime = datetime.datetime.now()
            mongo_repo: MoonRepo = MoonRepo()
            res = await mongo_repo.create(date=date, image=images.base_img.url)
            result: List[MoonModel] = await mongo_repo.all()

            with pytest.raises(IntegrityError):
                await mongo_repo.save(date=date, image=images.base_img.url)
            assert res.pk
            assert len(result) == 1
            assert str(date) == str(res.date)
