import pygame as pg

from config import (
    GRAY_LIGHT,
)


class Wall():

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self, screen):
        pg.draw.line(screen, GRAY_LIGHT,
                     (self.x1, self.y1), (self.x2, self.y2), 2)
