import os

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.orm import registry
from tortoise import fields
from tortoise.models import Model

from repos.schemas import extra_models
from settings import Settings
from utils.exceptions import NoImageFoundException

settings: Settings = Settings()
mapper_registry = registry()
Base = mapper_registry.generate_base()


class Coords(PydanticBaseModel):
    latitude: float
    longitude: float


def extra_params_validator(**kwargs) -> dict:
    if "image" in kwargs and isinstance(kwargs["image"], str):
        image_path: str = kwargs["image"]
        if not os.path.exists(image_path):
            raise NoImageFoundException
        with open(image_path, "rb") as f:
            image_data = f.read()
        kwargs["image"] = image_data

    return kwargs


class BaseModel(Model):
    @classmethod
    async def create(cls, **kwargs):
        kwargs = extra_params_validator(**kwargs)
        return await super().create(**kwargs)

    async def save(self, **kwargs):
        kwargs = extra_params_validator(**kwargs)
        return await super().save(**kwargs)

    class Meta:
        abstract = True


class MoonModel(BaseModel):
    date = fields.DateField(unique=True)
    image = extra_models.FileField(upload_to=os.path.join(settings.MEDIA, "moon"))
    created = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "moon"
        abstract = False


# await MoonModel.create(date=datetime.now(), image='base.png', name='NOWEEEEE Moon')
