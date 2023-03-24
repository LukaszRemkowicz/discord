import os

from PIL import Image

from repos.repo_types import UmMeteoGram


def create_images(tmp_dir):
    utils_dir = os.path.join(tmp_dir, "utils")
    os.makedirs(utils_dir)
    base_img = os.path.join(utils_dir, "base.png")
    img = Image.new("RGB", (300, 100), color="white")
    img.save(base_img)
    setattr(img, "url", base_img)
    setattr(img, "root_path", utils_dir)

    my_image = os.path.join(tmp_dir, "my_image.png")
    second_img = Image.new("RGB", (100, 100), color="white")
    second_img.save(my_image)
    setattr(second_img, "url", my_image)
    setattr(second_img, "root_path", utils_dir)

    return UmMeteoGram(base_img=img, extra_img=second_img)
