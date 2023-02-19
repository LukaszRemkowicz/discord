from typing import List

from repos.models import MoonModel


class MoonRepo:
    @staticmethod
    async def filter(**kwargs) -> List[MoonModel]:
        res = await MoonModel.filter(**kwargs)

        return res
