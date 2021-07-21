import pygame as pg

from config import (
    GRAY
)


class Wall(pg.sprite.Sprite):

    def __init__(self, _game, _x, _y, _width, _height):
        pg.sprite.Sprite.__init__(self)

        self.game = _game
        # Real position of the wall in the game world
        self.x = _x
        self.y = _y
        self.width = _width
        self.height = _height

        self.image = pg.Surface([self.width, self.height])
        self.image.fill(GRAY)
        self.mask = pg.mask.from_surface(self.image)
        self.mask.fill()
        self.rect = self.image.get_rect()

        # Set position for drawing only
        self.rect.x = self.x
        self.rect.y = self.y

        self.wall_segments = []
        self.wall_segments.append(
            WallSegment(self.x, self.y, self.x + self.width, self.y))
        self.wall_segments.append(
            WallSegment(self.x + self.width, self.y, self.x + self.width,
                        self.y + self.height))
        self.wall_segments.append(
            WallSegment(self.x + self.width, self.y + self.height, self.x,
                        self.y + self.height))
        self.wall_segments.append(
            WallSegment(self.x, self.y + self.height, self.x, self.y))

    def update(self):
        # Update x, y position of the rect for drawing only
        self.rect.x = round(self.rect.x + self.game.dx)
        self.rect.y = round(self.rect.y + self.game.dy)

    def get_wall_points(self):
        return ((self.x, self.y),
                (self.x + self.width, self.y),
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height))


class WallSegment():

    """
    Simple helper class to wrap all wall segment (line element)
    of the wall (rectangle). So each wall has 4 wall segments.
    """

    def __init__(self, _x1, _y1, _x2, _y2):
        self.x1 = _x1
        self.y1 = _y1
        self.x2 = _x2
        self.y2 = _y2
