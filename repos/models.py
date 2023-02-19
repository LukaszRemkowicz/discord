import os

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.ext.declarative import declarative_base
from tortoise import fields
from tortoise.models import Model
from repos.schemas import extra_models
from settings import MEDIA

Base = declarative_base()


class Coords(PydanticBaseModel):
    latitude: float
    longitude: float


class BaseModel(Model):
    @classmethod
    async def create(cls, **kwargs):
        if "image" in kwargs and isinstance(kwargs["image"], str):
            image_path = kwargs["image"]
            if not os.path.exists(image_path):
                open(image_path, "w").close()
            with open(image_path, "rb") as f:
                image_data = f.read()
            kwargs["image"] = image_data
        return await super().create(**kwargs)

    class Meta:
        abstract = True


class MoonModel(BaseModel):
    date = fields.DatetimeField()
    image = extra_models.FileField(upload_to=os.path.join(MEDIA, 'moon'))
    created = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "moon"
        abstract = False


# await MoonModel.create(date=datetime.now(), image='base.png', name='NOWEEEEE Moon')