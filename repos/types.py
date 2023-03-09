from collections import namedtuple

CropParams: namedtuple = namedtuple("MeteoBlueCrop", "top, right, bottom, left")
Coords2Points = namedtuple("Coords2Points", "act_x, act_y")
UmMeteoGram = namedtuple("UmMeteoGram", "base_img, extra_img")
