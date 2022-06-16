import os

import pygame as pg
from pygame.locals import RLEACCEL

from config import IMAGE_DIR, SOUND_DIR


def load_image(name, alpha=False, colorkey=None, path=True):
    if path:
        # create a full pathname to the file
        fullname = os.path.join(IMAGE_DIR, name)
    else:
        fullname = name
    try:
        image = pg.image.load(fullname)
    except pg.error as message:
        print("Cannot load image:", fullname)
        raise SystemExit(message)
    # makes a new copy of a Surface and converts its
    # color format and depth to match the display
    if alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()


def load_sound(name, path=True):
    class NoneSound:
        def play(self):
            pass

    if not pg.mixer:
        return NoneSound()

    if path:
        # create a full pathname to the file
        fullname = os.path.join(SOUND_DIR, name)
    else:
        fullname = name
    try:
        sound = pg.mixer.Sound(fullname)
    except pg.error as message:
        print("Cannot load sound:", fullname)
        raise SystemExit(message)

    return sound
