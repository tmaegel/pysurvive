#!/usr/bin/env python
# coding=utf-8
import sys
from typing import Union

import pygame as pg
from pygame.locals import RLEACCEL

from pysurvive.logger import Logger

logger = Logger()


class NoneSound:
    def play(self) -> None:
        pass


def load_image(
    filename: str, alpha: bool = False, colorkey: tuple[int, int, int] = None
) -> tuple[pg.surface.Surface, pg.rect.Rect]:
    """
    Load an image from disk.

    Args:
        filename (str): The filename including the path to load the image.
        alpha (bool): For alpha transparency, like in .png images, use the
            convert_alpha() method after loading so that the image has per
            pixel transparency. Default to False.
        colorkey (tuple[int, int, int]): Is only used if alpha is set to False.
            The color with the value is not displayed. Default to None.

    Returns:
        Image, Rect (tuple[Surface, Rect]): The image and the rect that represents it.
    """
    logger.debug("Loading image from file %s.", filename)
    try:
        image = pg.image.load(filename)
    except pg.error as message:
        logger.error("Error while loading image %s: %s", filename, message)
        sys.exit(1)
    # Makes a new copy of a Surface and converts its color format and
    # depth to match the display.
    if alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()


def load_sound(filename: str) -> Union[pg.mixer.Sound, NoneSound]:
    """
    Load a sound from disk.

    Args:
        filename (str): The filename including the path to load the sound.

    Returns:
        Sound object (Sound): The sound object.
    """
    if not pg.mixer:
        return NoneSound()
    try:
        sound = pg.mixer.Sound(filename)
    except pg.error as message:
        logger.error("Error while loading image %s:%s", filename, message)
        sys.exit(1)

    return sound
