from ImageUtility import *

def clampPixelToNBits(color: RGBA_Pixel, n: int) -> RGBA_Pixel:
    # NOTE: Alpha is weird about this. Just think of RGB for now
    bitsPerColor: int = n // 3
    return (representColorWithNBits(color[0], bitsPerColor),
            representColorWithNBits(color[1], bitsPerColor),
            representColorWithNBits(color[2], bitsPerColor),
            representColorWithNBits(color[3], bitsPerColor))


def representColorWithNBits(colorValue: int, n: int) -> int:
    # Each color will have n bits to represent it
    # 2^8 = 256 (true color)
    # 2^1 = 2 (black or color)
    n = clamp(n, 1, 8)
    targetMultiple = 2 ** (8 - n)
    return clamp(findClosestMultiple(colorValue, targetMultiple), 0, 256)


def clampToGbaPalette(color: RGBA_Pixel) -> RGBA_Pixel:
    # GBA has 15 bit RGB pallet
    # https://en.wikipedia.org/wiki/List_of_monochrome_and_RGB_color_formats#15-bit_RGB
    return clampPixelToNBits(color, 15)


def clamp(value: int, min_: int, max_: int) -> int:
    return max(min_, min(value, max_))


def findClosestMultiple(value: int, n: int) -> int:
    halfNMinus1: int = (n // 2) - 1
    valueModN: int = value % n
    if valueModN <= halfNMinus1:
        return value - valueModN
    else:
        return value + valueModN
