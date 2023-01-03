#!/usr/bin/env python
# coding=utf-8
import os
import sys

import pygame as pg
from pygame.locals import SRCALPHA

from pysurvive.utils import load_image

SPRITE_SIZE = 512


def load_spritesheet_from_filelist(files_path: str) -> list[pg.Surface]:
    sprite_table = []
    if not os.path.isdir(files_path):
        print(f"Directory {files_path} doesnt exists.")
        sys.exit(1)

    path, _, files = next(os.walk(files_path))
    for img in sorted(files):
        if not img.endswith(".png") or img.startswith("spritesheet"):
            continue

        print("Proccessing file", img)
        image, sprite_rect = load_image(f"{path}/{img}", alpha=True)
        sprite_image = pg.Surface((SPRITE_SIZE, SPRITE_SIZE), flags=SRCALPHA)
        # Center original sprite on new sprite.
        sprite_image.blit(
            image,
            (
                SPRITE_SIZE // 2 - sprite_rect.width // 2,
                SPRITE_SIZE // 2 - sprite_rect.height // 2,
            ),
        )
        sprite_table.append(sprite_image)

    return sprite_table


def main() -> None:
    """
    Script expect 2 positional arguments:
        * 1. The path of the list of sprites (files).
    """
    args = sys.argv[1:]
    try:
        sprites_path = args[0]
    except IndexError:
        print("ERROR: Invalid number of arguments.")
        sys.exit(1)

    spritesheet_table = load_spritesheet_from_filelist(sprites_path)
    spritesheet_image = pg.Surface(
        (SPRITE_SIZE * len(spritesheet_table), SPRITE_SIZE), flags=SRCALPHA
    )

    for x, sprite_img in enumerate(spritesheet_table):
        spritesheet_image.blit(
            sprite_img,
            (x * SPRITE_SIZE, 0),
        )
    pg.image.save(spritesheet_image, f"{sprites_path}/spritesheet.png")


if __name__ == "__main__":
    pg.init()
    _ = pg.display.set_mode((800, 600), pg.HIDDEN)
    main()
