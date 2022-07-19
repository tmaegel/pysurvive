#!/usr/bin/env python
# coding=utf-8
import os
import sys

import pygame as pg
from pygame.locals import SRCALPHA

from pysurvive.utils import load_image


def load_tile_from_filelist(files_path: str, tile_size: int) -> list[pg.Surface]:
    tile_table = []
    if not os.path.isdir(files_path):
        print(f"Directory {files_path} doesnt exists.")
        sys.exit(1)

    path, _, files = next(os.walk(files_path))
    for img in sorted(files):
        if not img.endswith(".png") or img.startswith("tilelist"):
            continue

        print("Proccessing file", img)
        tile_image, tile_rect = load_image(f"{path}/{img}", alpha=True)
        if tile_rect.width != tile_size or tile_rect.height != tile_size:
            print(
                "ERROR: The size of the tiles are not equal to the specific tile size."
            )
            sys.exit(1)
        tile_table.append(tile_image)

    return tile_table


def main() -> None:
    """
    Script expect 2 positional arguments:
        * 1. The path of the list of tiles (files).
        * 2. The tile size in pixel.
    """
    args = sys.argv[1:]
    try:
        tileset_path = args[0]
        tile_size = int(args[1])
    except IndexError:
        print("ERROR: Invalid number of arguments.")
        sys.exit(1)

    tileset_table = load_tile_from_filelist(tileset_path, tile_size)
    tileset_image = pg.Surface(
        (tile_size * len(tileset_table), tile_size), flags=SRCALPHA
    )

    for x, tile_img in enumerate(tileset_table):
        tileset_image.blit(
            tile_img,
            (x * tile_size, 0),
        )
    pg.image.save(tileset_image, f"{tileset_path}/tilelist.png")


if __name__ == "__main__":
    pg.init()
    _ = pg.display.set_mode((800, 600), pg.HIDDEN)
    main()
