from PIL import Image
from typing import Tuple, Set, List

from ImageUtility import *
from ColorPalette import ColorPalette
from ClampColorPalette import ClampColorPalette
from MathUtility import *


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


def cleanPixelArt(image: Image.Image, colorPalette: ColorPalette) -> Image.Image:
    initial_x, initial_y = image.size
    smallest_side_len: int = 2 ** 6  # 2^6=64  2^7=128  2^7=246
    smallImg: Image.Image = resizeImg(
        image, smallest_side_len, smallest_side_len, Image.BILINEAR)
    pallet_img: Image.Image = apply_function_to_image(
        smallImg, colorPalette.find_nearest_color)
    # pallet_img: Image.Image = apply_function_to_image(
    #     smallImg, clampToGbaPalette)
    transparentImg: Image.Image = flood_fill_transparency(
        pallet_img, (0, 0), pallet_img.getpixel((0, 0)), 30)
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


if __name__ == "__main__":
    # image_path = "./sailor hat icon, pixel art video game.jpeg"
    # image_path = "./otter creature from a RPG game, pixel art sprite.jpeg"
    image_path = "./a Pokémon first evolution form based on an otters from a RPG game.jpeg"

    # colorPalette: ColorPalette = ColorPalette.create_from_file(
    #     "./ColorPalettes/pokemon-ruby-sapphire-exterior.hex")
    colorPalette: ColorPalette = ColorPalette.create_from_file(
        "./ColorPalettes/ancient-scroll.hex")
    colorPalette: ClampColorPalette = ClampColorPalette(3 * 3)

    with Image.open(image_path) as image:
        clean_img: Image.Image = cleanPixelArt(image, colorPalette)
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
