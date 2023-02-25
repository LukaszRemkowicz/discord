import datetime
import tempfile
from typing import List

import pytest
from tortoise.exceptions import IntegrityError

from repos.db_repo import MoonRepo
from repos.models import MoonModel
from repos.types import UmMeteoGram
from tests.tests_utils import create_images
from utils.db_utils import DBConnectionHandler


@pytest.mark.asyncio
async def test_db_repo() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        images: UmMeteoGram = create_images(tmp_dir)

        mongo_repo: MoonRepo = MoonRepo()
        async with DBConnectionHandler():
            date: datetime = datetime.datetime.now()
            res = await mongo_repo.create(date=date, image=images.base_img.url)
            result: List[MoonModel] = await mongo_repo.all()

            with pytest.raises(IntegrityError):
                await mongo_repo.save(date=date, image=images.base_img.url)
            assert res.pk
            assert len(result) == 1
            assert str(date) == str(res.date)
