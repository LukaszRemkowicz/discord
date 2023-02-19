from collections import namedtuple

Coords: namedtuple = namedtuple("Coords", "lat, long")
CropParams: namedtuple = namedtuple("MeteoBlueCrop", "top, right, bottom, left")
Coords2Points = namedtuple("Coords2Points", "act_x, act_y")
