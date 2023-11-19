import os
import uuid
from io import BytesIO
from typing import Optional, Union

from PIL import Image
from tortoise import fields

from settings import settings
from utils.exceptions import UploadToNotGivenException


class FileField(fields.TextField):
    """FileField is a field that stores a file path to a file on the server."""

    def __init__(self, **kwargs) -> None:
        self.upload_to: str = kwargs.pop("upload_to")

        # If upload_to is not given, raise an exception.
        if not self.upload_to:
            raise UploadToNotGivenException

        path: str = os.path.join(settings.ROOT_PATH, self.upload_to)
        if not os.path.exists(path):
            os.makedirs(path)

        super().__init__(**kwargs)

    @property
    def upload_to_getter(self) -> str:
        """Returns the upload_to path."""
        return self.upload_to

    def to_db_value(self, value: Union[str, bytes, None], instance) -> Optional[str]:
        """Convert the value to a string and return the path to the file."""
        if isinstance(value, Image.Image):
            path: str = os.path.join(self.upload_to_getter, f"{uuid.uuid4()}.png")
            value.save(path)
            return path
        return super().to_db_value(value, instance)

    def to_python_value(
        self, value: Union[bytes, str]
    ) -> Optional[Union[Image.Image, str]]:
        """Convert the value to an Image object and return it."""
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
    def upload_to_getter(self, value) -> None:
        """Set the upload_to path."""
        self._upload_to = value


class MyModel:
    FileField = FileField


extra_models = MyModel()
