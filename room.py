import pygame as pg

from class_toolchain import Block
from utils import load_image


class Room(pg.sprite.Sprite):

    scale_px = 512
    wall_size = 25
    door_size = 100

    texture_path = 'textures/brick/ground_02.png'

    def __init__(self, _x, _y, _width, _height, _xoffset, _yoffset,
                 _doors=(), _no_walls=()):
        pg.sprite.Sprite.__init__(self)

        # Real position of the room in the game world.
        self.x = _x
        self.y = _y
        self.width = _width
        self.height = _height
        self.doors = _doors
        self.no_walls = _no_walls

        self.image = pg.Surface([self.width, self.height])
        self.rect = self.image.get_rect()

        # Set the initial position for drawing only
        self.rect.x = self.x - _xoffset
        self.rect.y = self.y - _yoffset

        self.texture_orig, _ = load_image(self.texture_path)
        self.texture = pg.transform.scale(
            self.texture_orig, (self.scale_px, self.scale_px))
        for x in range(0, self.rect.width, self.scale_px):
            for y in range(0, self.rect.height, self.scale_px):
                self.image.blit(self.texture, (x, y))

        # self.wall_color = self.image.get_at((0, 0))
        self.wall_color = (88, 77, 64)

        self.walls = []
        if 'top' not in self.no_walls:
            # 1: Door in the top
            if 'top' not in self.doors:
                self.walls.append(Wall(self.x,
                                       self.y,
                                       self.width,
                                       self.wall_size,
                                       self.wall_color,
                                       _xoffset,
                                       _yoffset))
            else:
                self.walls.append(Wall(self.x,
                                       self.y,
                                       self.width//2 - self.door_size//2,
                                       self.wall_size,
                                       self.wall_color,
                                       _xoffset,
                                       _yoffset))
                self.walls.append(Wall(self.x + self.width//2 + self.door_size//2,
                                       self.y,
                                       self.width//2 - self.door_size//2,
                                       self.wall_size,
                                       self.wall_color,
                                       _xoffset,
                                       _yoffset))
        if 'bottom' not in self.no_walls:
            # 2: Door on the bottom
            if 'bottom' not in self.doors:
                self.walls.append(Wall(self.x,
                                       self.y + self.height - self.wall_size,
                                       self.width,
                                       self.wall_size,
                                       self.wall_color,
                                       _xoffset,
                                       _yoffset))
            else:
                self.walls.append(Wall(self.x,
                                       self.y + self.height - self.wall_size,
                                       self.width//2 - self.door_size//2,
                                       self.wall_size,
                                       self.wall_color,
                                       _xoffset,
                                       _yoffset))
                self.walls.append(Wall(self.x + self.width//2 + self.door_size//2,
                                       self.y + self.height - self.wall_size,
                                       self.width//2 - self.door_size//2,
                                       self.wall_size,
                                       self.wall_color,
                                       _xoffset,
                                       _yoffset))
        if 'left' not in self.no_walls:
            # 3: Door in the left
            if 'left' not in self.doors:
                self.walls.append(Wall(self.x,
                                       self.y + self.wall_size,
                                       self.wall_size,
                                       self.height - self.wall_size * 2,
                                       self.wall_color,
                                       _xoffset,
                                       _yoffset))
            else:
                self.walls.append(Wall(self.x,
                                       self.y + self.wall_size,
                                       self.wall_size,
                                       self.height//2 - self.wall_size
                                       - self.door_size//2,
                                       self.wall_color,
                                       _xoffset,
                                       _yoffset))
                self.walls.append(Wall(self.x,
                                       self.y + self.height//2 + self.door_size//2,
                                       self.wall_size,
                                       self.height//2 - self.wall_size
                                       - self.door_size//2,
                                       self.wall_color,
                                       _xoffset,
                                       _yoffset))
        if 'right' not in self.no_walls:
            # 4: Door on the right
            if 'right' not in self.doors:
                self.walls.append(Wall(self.x + self.width - self.wall_size,
                                       self.y + self.wall_size,
                                       self.wall_size,
                                       self.height - self.wall_size * 2,
                                       self.wall_color,
                                       _xoffset,
                                       _yoffset))
            else:
                self.walls.append(Wall(self.x + self.width - self.wall_size,
                                       self.y + self.wall_size,
                                       self.wall_size,
                                       self.height//2 - self.wall_size
                                       - self.door_size//2,
                                       self.wall_color,
                                       _xoffset,
                                       _yoffset))
                self.walls.append(Wall(self.x + self.width - self.wall_size,
                                       self.y + self.height//2 + self.door_size//2,
                                       self.wall_size,
                                       self.height//2 - self.wall_size
                                       - self.door_size//2,
                                       self.wall_color,
                                       _xoffset,
                                       _yoffset))

    def update(self, _dx, _dy):
        # Update x, y position of the rect for drawing only.
        self.rect.x = round(self.rect.x + _dx)
        self.rect.y = round(self.rect.y + _dy)

    def get_door(self):
        doors = []
        if 'top' in self.doors:
            doors.append(pg.Rect(
                self.x + self.width//2 - self.door_size//2,
                self.y,
                self.door_size,
                self.wall_size))
        if 'bottom' in self.doors:
            doors.append(pg.Rect(
                self.x + self.width//2 - self.door_size//2,
                self.y + self.height - self.wall_size,
                self.door_size,
                self.wall_size))
        if 'left' in self.doors:
            doors.append(pg.Rect(
                self.x,
                self.y + self.height//2 - self.door_size//2,
                self.wall_size,
                self.door_size))
        if 'right' in self.doors:
            doors.append(pg.Rect(
                self.x + self.width - self.wall_size,
                self.y + self.height//2 - self.door_size//2,
                self.wall_size,
                self.door_size))

        return doors


class Wall(Block):

    def __init__(self, _x, _y, _width, _height, _color,
                 _xoffset, _yoffset):
        Block.__init__(self, _x, _y, _width,
                       _height, _xoffset, _yoffset)
        self.image.fill(_color)


class Box(Block):

    texture_path = 'objects/block/box_01.png'

    def __init__(self, _x, _y, _size, _xoffset, _yoffset):
        Block.__init__(self, _x, _y, _size, _size, _xoffset, _yoffset)

        self.texture_orig, _ = load_image(self.texture_path)
        self.texture = pg.transform.scale(
            self.texture_orig, (self.width, self.height))
        self.image.blit(self.texture, (0, 0))
