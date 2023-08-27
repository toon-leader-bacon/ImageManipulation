from PIL import Image
from typing import Tuple, Set, List

XY_Coord = Tuple[int, int]
RGB_Pixel = Tuple[int, int, int]
RGBA_Pixel = Tuple[int, int, int, int]


def upscale_image(image: Image.Image,
                  scale_factor: int,
                  resample_alg: Image.Resampling = Image.BOX) -> Image.Image:
    (new_width, new_height) = \
        (image.width * scale_factor, image.height * scale_factor)

    resized_image: Image.Image = image.resize(
        (new_width, new_height), resample_alg)
    return resized_image


def downscale_image(image: Image.Image,
                    scale_factor: int,
                    resample_alg: Image.Resampling = Image.BOX) -> Image.Image:
    (new_width, new_height) = \
        (image.width // scale_factor, image.height // scale_factor)
    return resizeImg(image, new_width, new_height, resample_alg)


def resizeImg(image: Image.Image,
              new_width: int,
              new_height: int,
              resample_alg: Image.Resampling = Image.BOX) -> Image.Image:
    resized_image: Image.Image = image.resize(
        (new_width, new_height), resample_alg)
    return resized_image


def cleanPixelArt(image: Image.Image) -> Image.Image:
    # TODO: Come up with the best enums for resizeImg resample_alg enum
    initial_x, initial_y = image.size
    smallest_side_len: int = 2 ** 6  # 2^6=64  2^7=128  2^7=246
    smallImg: Image.Image = resizeImg(image, smallest_side_len, smallest_side_len, Image.BOX)
    # colorPalette: ColorPalette = ColorPalette.create_from_file(
    #     "./pokemon-ruby-sapphire-exterior.hex")
    # pallet_img: Image.Image = apply_function_to_image(
    #     smallImg, colorPalette.find_nearest_color)
    pallet_img: Image.Image = apply_function_to_image(
        smallImg, clampToGbaPalette)
    transparentImg: Image.Image = flood_fill_transparency(
        pallet_img, (0, 0), image.getpixel((0, 0)), 30)
    return resizeImg(transparentImg, initial_x, initial_y, Image.NEAREST)


def apply_function_to_image(input_img: Image.Image, mod_func) -> Image.Image:
    result_image: Image.Image = input_img.convert("RGBA")
    for y in range(result_image.height):
        for x in range(result_image.width):
            old_pixel: RGBA_Pixel = result_image.getpixel((x, y))
            new_pixel: RGBA_Pixel = mod_func(old_pixel)
            result_image.putpixel((x, y), new_pixel)
    return result_image


def flood_fill_transparency(input_img: Image.Image,
                            start_coord: XY_Coord,
                            target_color: RGB_Pixel,
                            tolerance: int = 10) -> Image.Image:
    result_img: Image.Image = input_img.convert("RGBA")
    width, height = result_img.size
    # data: Image._PixelAccessor = result_img.load()

    frontier: XY_Coord = []
    frontier.append(start_coord)
    visited: Set[RGB_Pixel] = set()

    while len(frontier) != 0:
        current_coord = frontier.pop()
        # print(f"current_coord: {current_coord}")
        x, y = current_coord
        if (x < 0) or (x >= width) or (y < 0) or (y >= height) or (x, y) in visited:
            continue

        # else new value to explore
        visited.add((x, y))
        pixel_color: RGB_Pixel = result_img.getpixel((x, y))  # data[x, y]
        if color_difference(pixel_color, target_color) > tolerance:
            # Edge pixel, do not process or add neighbors
            continue

        # Else flood fill color, change alpha
        result_img.putpixel(
            (x, y), (pixel_color[0], pixel_color[1], pixel_color[2], 0))
        # data[(x, y)] = (pixel_color[0], pixel_color[1], pixel_color[2], 0)

        # Add neighbors to frontier
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            neighbor: XY_Coord = (x + dx, y + dy)
            if not (neighbor in visited):
                # print(f"Adding neighbor {neighbor}")
                # Append, not extend
                frontier.append(neighbor)

    return result_img


def color_difference(color1: RGB_Pixel,
                     color2: RGB_Pixel) -> int:
    # Manhattan distance
    return sum(abs(c1 - c2) for c1, c2 in zip(color1, color2))


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


def clamp(value: int, min_: int, max_: int):
    return max(min_, min(value, max_))


def findClosestMultiple(value: int, n: int) -> int:
    halfNMinus1: int = (n // 2) - 1
    valueModN: int = value % n
    if valueModN <= halfNMinus1:
        return value - valueModN
    else:
        return value + valueModN


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


if __name__ == "__main__":
    image_path = "./sailor hat icon, pixel art video game.jpeg"

    with Image.open(image_path) as image:
        clean_img: Image.Image = cleanPixelArt(image)
        clean_img.show()

        # print("Initial image")
        # image.show()

        # print("down scaled image")
        # downImg = downscale_image(
        #     image, scale_factor=4, resample_alg=Image.NEAREST)
        # downImg.show()

        # print("flood fill image")
        # floodImg = flood_fill_transparency(downImg, (0, 0), image.getpixel((0, 0)), 10)

        # print("flood fill image finished")
        # floodImg.show()
        # print("exiting")
