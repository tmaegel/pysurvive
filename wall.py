import pygame as pg

from config import (
    GRAY_LIGHT,
)


class Wall():

    def __init__(self, _x1, _y1, _x2, _y2):
        self.x1 = _x1
        self.y1 = _y1
        self.x2 = _x2
        self.y2 = _y2

    def draw(self, screen):
        pg.draw.line(screen, GRAY_LIGHT,
                     (self.x1, self.y1), (self.x2, self.y2), 2)
