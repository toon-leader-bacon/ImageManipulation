from ImageUtility import *
from MathUtility import *


class ClampColorPalette:
    def __init__(self, bitsPerRGBPixel: int = 15) -> None:
        # GBA has 15 bits per rgb => 5 bits per color channel => 32 * 32 * 32 total pixels
        self.bitsPerPixel = bitsPerRGBPixel

    def find_nearest_color(self, colorToCheck: RGB_Pixel) -> RGB_Pixel:
        return clampPixelToNBits(colorToCheck, self.bitsPerPixel)
