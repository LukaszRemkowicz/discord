import os
import uuid
from io import BytesIO
from typing import Union, Optional

from PIL import Image
from tortoise import fields

from settings import Settings
from utils.exceptions import UploadToNotGivenException


class FileField(fields.TextField):
    def __init__(self, **kwargs) -> None:
        self.upload_to: str = kwargs.pop("upload_to", ".")

        if not self.upload_to:
            raise UploadToNotGivenException

        path: str = os.path.join(Settings().ROOT_PATH, self.upload_to)
        if not os.path.exists(path):
            os.makedirs(path)

        super().__init__(**kwargs)

    @property
    def upload_to_getter(self):
        return self.upload_to

    def to_db_value(self, value: Union[str, bytes, None], instance) -> Optional[str]:
        if isinstance(value, Image.Image):
            path: str = os.path.join(self.upload_to_getter, f"{uuid.uuid4()}.png")
            value.save(path)
            return path
        return super().to_db_value(value, instance)

    def to_python_value(
        self, value: Union[bytes, str]
    ) -> Optional[Union[Image.Image, str]]:
        if isinstance(value, str):
            path: str = value
            with open(value, "rb") as f:
                value: bytes = f.read()
                img: Image = Image.open(BytesIO(value))
                setattr(img, "url", path)
                return img
        img: Image = Image.open(BytesIO(value))
        return img

    @upload_to_getter.setter
    def upload_to_getter(self, value):
        self._upload_to = value


class MyModel:
    FileField = FileField


extra_models = MyModel()
