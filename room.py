import pygame as pg

from utils import load_image


class Room(pg.sprite.Sprite):

    scale_px = 256

    def __init__(self, _game, _x, _y, _width, _height, _texture):
        pg.sprite.Sprite.__init__(self)

        self.game = _game
        # Real position of the room in the game world
        self.x = _x
        self.y = _y
        self.width = _width
        self.height = _height

        self.image = pg.Surface([self.width, self.height])
        self.rect = self.image.get_rect()

        # Set position for drawing only
        self.rect.x = self.x
        self.rect.y = self.y

        self.texture_orig, _ = load_image(_texture)
        self.texture = pg.transform.scale(
            self.texture_orig, (self.scale_px, self.scale_px))
        for x in range(0, self.rect.width, self.scale_px):
            for y in range(0, self.rect.height, self.scale_px):
                self.image.blit(self.texture, (x, y))

    def update(self):
        # Update x, y position of the rect for drawing only
        self.rect.x += self.game.dx
        self.rect.y += self.game.dy
