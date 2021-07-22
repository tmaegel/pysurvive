import pygame as pg

from class_toolchain import Block
from utils import load_image


class Room(pg.sprite.Sprite):

    scale_px = 512
    wall_size = 15
    door_size = 100

    texture_path = 'textures/brick/ground_02.png'

    def __init__(self, _game, _x, _y, _width, _height, _door):
        pg.sprite.Sprite.__init__(self)

        self.game = _game
        # Real position of the room in the game world
        self.x = _x
        self.y = _y
        self.width = _width
        self.height = _height
        self.door = _door

        self.image = pg.Surface([self.width, self.height])
        self.rect = self.image.get_rect()

        # Set position for drawing only
        self.rect.x = self.x
        self.rect.y = self.y

        self.texture_orig, _ = load_image(self.texture_path)
        self.texture = pg.transform.scale(
            self.texture_orig, (self.scale_px, self.scale_px))
        for x in range(0, self.rect.width, self.scale_px):
            for y in range(0, self.rect.height, self.scale_px):
                self.image.blit(self.texture, (x, y))

        # self.wall_color = self.image.get_at((0, 0))
        self.wall_color = (88, 77, 64)

        self.walls = []
        # 1: Door in the top
        if 'top' not in self.door:
            self.walls.append(Wall(self.game,
                                   self.x,
                                   self.y,
                                   self.width,
                                   self.wall_size,
                                   self.wall_color))
        else:
            self.walls.append(Wall(self.game,
                                   self.x,
                                   self.y,
                                   self.width//2 - self.door_size//2,
                                   self.wall_size,
                                   self.wall_color))
            self.walls.append(Wall(self.game,
                                   self.x + self.width//2 + self.door_size//2,
                                   self.y,
                                   self.width//2 - self.door_size//2,
                                   self.wall_size,
                                   self.wall_color))
        # 2: Door on the bottom
        if 'bottom' not in self.door:
            self.walls.append(Wall(self.game,
                                   self.x,
                                   self.y + self.height - self.wall_size,
                                   self.width,
                                   self.wall_size,
                                   self.wall_color))
        else:
            self.walls.append(Wall(self.game,
                                   self.x,
                                   self.y + self.height - self.wall_size,
                                   self.width//2 - self.door_size//2,
                                   self.wall_size,
                                   self.wall_color))
            self.walls.append(Wall(self.game,
                                   self.x + self.width//2 + self.door_size//2,
                                   self.y + self.height - self.wall_size,
                                   self.width//2 - self.door_size//2,
                                   self.wall_size,
                                   self.wall_color))
        # 3: Door in the left
        if 'left' not in self.door:
            self.walls.append(Wall(self.game,
                                   self.x,
                                   self.y + self.wall_size,
                                   self.wall_size,
                                   self.height - self.wall_size * 2,
                                   self.wall_color))
        else:
            self.walls.append(Wall(self.game,
                                   self.x,
                                   self.y + self.wall_size,
                                   self.wall_size,
                                   self.height//2 - self.wall_size
                                   - self.door_size//2,
                                   self.wall_color))
            self.walls.append(Wall(self.game,
                                   self.x,
                                   self.y + self.height//2 + self.door_size//2,
                                   self.wall_size,
                                   self.height//2 - self.wall_size
                                   - self.door_size//2,
                                   self.wall_color))
        # 4: Door on the right
        if 'right' not in self.door:
            self.walls.append(Wall(self.game,
                                   self.x + self.width - self.wall_size,
                                   self.y + self.wall_size,
                                   self.wall_size,
                                   self.height - self.wall_size * 2,
                                   self.wall_color))
        else:
            self.walls.append(Wall(self.game,
                                   self.x + self.width - self.wall_size,
                                   self.y + self.wall_size,
                                   self.wall_size,
                                   self.height//2 - self.wall_size
                                   - self.door_size//2,
                                   self.wall_color))
            self.walls.append(Wall(self.game,
                                   self.x + self.width - self.wall_size,
                                   self.y + self.height//2 + self.door_size//2,
                                   self.wall_size,
                                   self.height//2 - self.wall_size
                                   - self.door_size//2,
                                   self.wall_color))

    def update(self):
        # Update x, y position of the rect for drawing only
        self.rect.x = round(self.rect.x + self.game.dx)
        self.rect.y = round(self.rect.y + self.game.dy)


class Wall(Block):

    def __init__(self, _game, _x, _y, _width, _height, _color):
        Block.__init__(self, _game, _x, _y, _width, _height)
        self.image.fill(_color)


class Box(Block):

    texture_path = 'objects/block/box_01.png'

    def __init__(self, _game, _x, _y, _size):
        Block.__init__(self, _game, _x, _y, _size, _size)

        self.texture_orig, _ = load_image(self.texture_path)
        self.texture = pg.transform.scale(
            self.texture_orig, (self.width, self.height))
        self.image.blit(self.texture, (0, 0))
