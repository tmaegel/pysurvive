#!/usr/bin/env python
# coding=utf-8
import pygame as pg

from .class_toolchain import Block
from .config import BLACK, GRAY_LIGHT2, GRAY_LIGHT3


class Room(pg.sprite.Sprite):

    scale_px = 512
    wall_size = 10
    door_size = 100

    def __init__(self, _x, _y, _width, _height, _offset, _doors=()):
        pg.sprite.Sprite.__init__(self)

        # Real position of the room in the game world.
        self.x = _x
        self.y = _y
        self.width = _width
        self.height = _height
        self.doors = _doors

        self.image = pg.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        # Set the initial position for drawing only.
        self.rect.x = self.x - _offset[0]
        self.rect.y = self.y - _offset[1]
        self.image.fill(GRAY_LIGHT3)

        self.walls = []
        # Two cornor walls at the top
        self.walls.append(
            Wall(self.x, self.y, self.wall_size, self.wall_size, _offset, ())
        )
        self.walls.append(
            Wall(
                self.x + self.width - self.wall_size,
                self.y,
                self.wall_size,
                self.wall_size,
                _offset,
                (),
            )
        )
        # Door in the top
        x = self.x + self.wall_size
        if "top" not in self.doors:
            self.walls.append(
                Wall(
                    x,
                    self.y,
                    self.width - self.wall_size * 2,
                    self.wall_size,
                    _offset,
                    ("bottom",),
                )
            )
        else:
            width = round((self.width - self.wall_size * 2) / 2 - self.door_size / 2)
            self.walls.append(
                Wall(x, self.y, width, self.wall_size, _offset, ("bottom", "right"))
            )
            self.walls.append(
                Wall(
                    x + width + self.door_size,
                    self.y,
                    width,
                    self.wall_size,
                    _offset,
                    ("bottom", "left"),
                )
            )

        # Two cornor walls at the bottom
        self.walls.append(
            Wall(
                self.x,
                self.y + self.height - self.wall_size,
                self.wall_size,
                self.wall_size,
                _offset,
                (),
            )
        )
        self.walls.append(
            Wall(
                self.x + self.width - self.wall_size,
                self.y + self.height - self.wall_size,
                self.wall_size,
                self.wall_size,
                _offset,
                (),
            )
        )
        # Door on the bottom
        x = self.x + self.wall_size
        y = self.y + self.height - self.wall_size
        if "bottom" not in self.doors:
            self.walls.append(
                Wall(
                    x,
                    y,
                    self.width - self.wall_size * 2,
                    self.wall_size,
                    _offset,
                    ("top",),
                )
            )
        else:
            width = round((self.width - self.wall_size * 2) / 2 - self.door_size / 2)
            self.walls.append(
                Wall(x, y, width, self.wall_size, _offset, ("top", "right"))
            )
            self.walls.append(
                Wall(
                    x + width + self.door_size,
                    y,
                    width,
                    self.wall_size,
                    _offset,
                    ("top", "left"),
                )
            )

        # Door in the left
        if "left" not in self.doors:
            self.walls.append(
                Wall(
                    self.x,
                    self.y + self.wall_size,
                    self.wall_size,
                    self.height - self.wall_size * 2,
                    _offset,
                    ("right",),
                )
            )
        else:
            self.walls.append(
                Wall(
                    self.x,
                    self.y + self.wall_size,
                    self.wall_size,
                    self.height // 2 - self.wall_size - self.door_size // 2,
                    _offset,
                    ("right", "bottom"),
                )
            )
            self.walls.append(
                Wall(
                    self.x,
                    self.y + self.height // 2 + self.door_size // 2,
                    self.wall_size,
                    self.height // 2 - self.wall_size - self.door_size // 2,
                    _offset,
                    ("right", "top"),
                )
            )

        # Door on the right
        if "right" not in self.doors:
            self.walls.append(
                Wall(
                    self.x + self.width - self.wall_size,
                    self.y + self.wall_size,
                    self.wall_size,
                    self.height - self.wall_size * 2,
                    _offset,
                    ("left",),
                )
            )
        else:
            self.walls.append(
                Wall(
                    self.x + self.width - self.wall_size,
                    self.y + self.wall_size,
                    self.wall_size,
                    self.height // 2 - self.wall_size - self.door_size // 2,
                    _offset,
                    ("left", "bottom"),
                )
            )
            self.walls.append(
                Wall(
                    self.x + self.width - self.wall_size,
                    self.y + self.height // 2 + self.door_size // 2,
                    self.wall_size,
                    self.height // 2 - self.wall_size - self.door_size // 2,
                    _offset,
                    ("left", "top"),
                )
            )

    def update(self, offset):
        # Update x, y position of the rect for drawing only.
        self.rect.x = round(self.x - offset[0])
        self.rect.y = round(self.y - offset[1])

    def get_door(self):
        doors = []
        if "top" in self.doors:
            doors.append(
                pg.Rect(
                    self.x + self.width // 2 - self.door_size // 2,
                    self.y,
                    self.door_size,
                    self.wall_size,
                )
            )
        if "bottom" in self.doors:
            doors.append(
                pg.Rect(
                    self.x + self.width // 2 - self.door_size // 2,
                    self.y + self.height - self.wall_size,
                    self.door_size,
                    self.wall_size,
                )
            )
        if "left" in self.doors:
            doors.append(
                pg.Rect(
                    self.x,
                    self.y + self.height // 2 - self.door_size // 2,
                    self.wall_size,
                    self.door_size,
                )
            )
        if "right" in self.doors:
            doors.append(
                pg.Rect(
                    self.x + self.width - self.wall_size,
                    self.y + self.height // 2 - self.door_size // 2,
                    self.wall_size,
                    self.door_size,
                )
            )

        return doors


class Wall(Block):

    thickness = 2

    def __init__(self, _x, _y, _width, _height, _sides, _offset):
        Block.__init__(self, _x, _y, _width, _height, _sides, _offset)

        self.image.fill(GRAY_LIGHT2)

        # Initial draw the wall segments in the image.
        self.draw()

    def draw(self) -> None:
        if "top" in self.sides:
            pg.draw.line(self.image, BLACK, (0, 0), (self.width, 0), self.thickness)
        if "right" in self.sides:
            pg.draw.line(
                self.image,
                BLACK,
                (self.width - self.thickness, 0),
                (self.width - self.thickness, self.height),
                self.thickness,
            )
        if "bottom" in self.sides:
            pg.draw.line(
                self.image,
                BLACK,
                (0, 0 + self.height - self.thickness),
                (self.width, 0 + self.height - self.thickness),
                self.thickness,
            )
        if "left" in self.sides:
            pg.draw.line(self.image, BLACK, (0, 0), (0, self.height), self.thickness)


class Box(Block):

    thickness = 2

    def __init__(self, _x, _y, _size, _offset):
        Block.__init__(self, _x, _y, _size, _size, _offset)

        self.image.fill(GRAY_LIGHT2)

        # Initial draw the wall segments in the image.
        self.draw()

    def draw(self) -> None:
        pg.draw.line(self.image, BLACK, (0, 0), (self.width, 0), self.thickness)
        pg.draw.line(
            self.image,
            BLACK,
            (self.width - self.thickness, 0),
            (self.width - self.thickness, self.height),
            self.thickness,
        )
        pg.draw.line(
            self.image,
            BLACK,
            (0, 0 + self.height - self.thickness),
            (self.width, 0 + self.height - self.thickness),
            self.thickness,
        )
        pg.draw.line(self.image, BLACK, (0, 0), (0, self.height), self.thickness)
