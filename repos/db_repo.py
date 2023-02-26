from typing import List

from logger import ColoredLogger, get_module_logger
from repos.models import MoonModel

logger: ColoredLogger = get_module_logger("MOON")


class MoonRepo:
    """Moon table repo. Handles basic CRUD operation"""

    model = MoonModel

    async def filter(self, **kwargs) -> List[MoonModel]:
        """Filter by given params."""
        res = await self.model.filter(**kwargs)

        return res

    async def create(self, **kwargs) -> MoonModel:
        """Save MoonModel instance to database"""
        res: MoonModel = await self.model.create(**kwargs)  # noqa
        logger.info(f"Object with id {res.pk} created")

        return res

    async def save(self, **kwargs) -> MoonModel:
        """Save MoonModel instance to database"""
        model: MoonModel = self.model(**kwargs)
        res: MoonModel = await model.save()  # noqa
        logger.info(f"Object with id {res.pk} created")

        return res

    async def all(self) -> List[MoonModel]:
        """Get all MoonModel instances from DB"""
        return await self.model.all()
