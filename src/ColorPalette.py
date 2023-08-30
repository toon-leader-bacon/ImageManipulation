from ImageUtility import *


class ColorPalette:
    def __init__(self) -> None:
        self.colors: Set[RGB_Pixel] = set()

    @staticmethod
    def create_from_set(colors: Set[RGB_Pixel]) -> "ColorPalette":
        result = ColorPalette()
        for value in colors:
            result.add(value)
        return result

    @staticmethod
    def create_from_file(file_path: str) -> "ColorPalette":
        result = ColorPalette()
        with open(file_path, 'r') as file:
            for line in file:
                result.add(hex_to_rgb(line.strip()))
        return result

    def add(self, colorToAdd: RGB_Pixel) -> None:
        self.colors.add(colorToAdd)

    def find_nearest_color(self, colorToCheck: RGB_Pixel) -> RGB_Pixel:
        closestDist: int = 999999
        closestPaletteColor: RGB_Pixel = (0, 0, 0)
        for paletteColor in self.colors:
            dist: int = color_difference(paletteColor, colorToCheck)
            if (dist < closestDist):
                closestDist = dist
                closestPaletteColor = paletteColor
        return closestPaletteColor


def hex_to_rgb(hex_value: str) -> RGB_Pixel:
    hex_value = hex_value.lstrip("#")
    return (int(hex_value[0:2], 16),
            int(hex_value[2:4], 16),
            int(hex_value[4:6], 16))
