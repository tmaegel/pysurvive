#!/usr/bin/env python
# coding=utf-8
import os
import sys
from typing import Tuple, Union

import pygame as pg
from pygame.locals import RLEACCEL

from .config import IMAGE_DIR, SOUND_DIR
from .logger import logger


class NoneSound:
    def play(self) -> None:
        pass


def load_image(
    name: str,
    alpha: bool = False,
    colorkey: Tuple[int, int, int] = None,
    path: bool = True,
) -> Tuple[pg.Surface, pg.Rect]:
    if path:
        # Create a full pathname to the file.
        fullname = os.path.join(IMAGE_DIR, name)
    else:
        fullname = name
    try:
        image = pg.image.load(fullname)
    except pg.error as message:
        logger.error("Erro while loading image %s: %s", fullname, message)
        sys.exit(1)
    # Makes a new copy of a Surface and converts its
    # color format and depth to match the display.
    if alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()


def load_sound(name: str, path: bool = True) -> Union[pg.mixer.Sound, NoneSound]:
    if not pg.mixer:
        return NoneSound()

    if path:
        # Create a full pathname to the file.
        fullname = os.path.join(SOUND_DIR, name)
    else:
        fullname = name
    try:
        sound = pg.mixer.Sound(fullname)
    except pg.error as message:
        logger.error("Erro while loading image %s: %s", fullname, message)
        sys.exit(1)

    return sound
