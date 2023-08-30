from PIL import Image
from typing import Tuple, Set, List

XY_Coord = Tuple[int, int]
RGB_Pixel = Tuple[int, int, int]
RGBA_Pixel = Tuple[int, int, int, int]


def color_difference(color1: RGB_Pixel,
                     color2: RGB_Pixel) -> int:
    # Manhattan distance
    return sum(abs(c1 - c2) for c1, c2 in zip(color1, color2))
