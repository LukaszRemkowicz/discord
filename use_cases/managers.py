import os

from PIL import Image

from settings import settings


class UMPhotoManager:
    @staticmethod
    def merge_photos(image1: Image, image2: Image) -> str:
        """Merge photos into one photo. Return path to new photo"""
        image1_width: int
        image1_height: int
        image2_width: int
        image2_height: int

        image1_width, image1_height = image1.size
        image2_width, image2_height = image2.size

        image1_width, image1_height = image1.size
        image2_width, image2_height = image2.size

        new_image: Image = Image.new("RGB", (image1_width + image2_width, image1_height))

        new_image.paste(image1, (0, 0))
        new_image.paste(image2, (image1_width, 0))
        new_path: str = os.path.join(settings.MEDIA, "merged_image.jpg")
        new_image.save(new_path, "png")

        return new_path
