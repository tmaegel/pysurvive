import os
import pygame as pg

from pygame.locals import RLEACCEL

from config import (
    ASSETS_DIR,
)


def load_image(name, alpha=True, colorkey=None):
    # create a full pathname to the file
    fullname = os.path.join(ASSETS_DIR + 'img/', name)
    try:
        image = pg.image.load(fullname)
    except pg.error as message:
        print('Cannot load image:', fullname)
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


def load_sound(name):
    class NoneSound:
        def play(self): pass

    if not pg.mixer:
        return NoneSound()

    # create a full pathname to the file
    fullname = os.path.join(ASSETS_DIR + 'sounds/', name)
    try:
        sound = pg.mixer.Sound(fullname)
    except pg.error as message:
        print('Cannot load sound:', fullname)
        raise SystemExit(message)

    return sound
