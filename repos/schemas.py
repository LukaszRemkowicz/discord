import os
import uuid
from io import BytesIO
from typing import Union, Optional

from PIL import Image
from tortoise import fields


class FileField(fields.TextField):
    def __init__(self, **kwargs) -> None:
        self.upload_to: str = kwargs.pop("upload_to", ".")
        super().__init__(**kwargs)

    def to_db_value(self, value: Union[str, bytes, None], instance) -> Optional[str]:
        if isinstance(value, Image.Image):
            path: str = os.path.join(self.upload_to, f"{uuid.uuid4()}.png")
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

    # def from_db_value(self, value: str, expression, connection) -> Optional[Image.Image]:
    #     super().from_db_value( value, expression, connection)
    #     if value:
    #         with open(value, 'rb') as f:
    #             img = Image.open(BytesIO(f.read()))
    #         return img
    #     return None


# class DateTimeField:
#     def __init__(self, auto_now_add=False, auto_now=False, *args, **kwargs):
#         self.auto_now_add = auto_now_add
#         self.auto_now = auto_now
#
#     def __call__(self):
#         if self.auto_now_add:
#             return fields.DatetimeField(auto_now_add=True)
#         elif self.auto_now:
#             return fields.DatetimeField(auto_now=True)
#         else:
#             return fields.DatetimeField()


class MyModel:
    FileField = FileField


extra_models = MyModel()
