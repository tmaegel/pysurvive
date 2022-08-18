#!/usr/bin/env python
# coding=utf-8
import pygame as pg

from pysurvive.config import SCREEN_RECT


class Screen:

    """
    Simple sprite that represent the screen and is used to detect
    wheather objects are visible on the screen.
    """

    _screen = None

    def __new__(cls, rect: pg.Rect = None):
        if cls._screen is None:
            cls._screen = super().__new__(cls)
            if rect:
                cls._screen.image = pg.Surface(rect.size)
                cls._screen.rect = rect
            else:
                cls._screen.image = pg.Surface(SCREEN_RECT.size)
                cls._screen.rect = SCREEN_RECT

        return cls._screen

    def __str__(self) -> str:
        return f"Screen (size={self.width}x{self.height})"

    @classmethod
    def delete(cls):
        cls._screen = None

    @property
    def size(self) -> tuple[int, int]:
        return self.rect.size

    @property
    def width(self) -> int:
        return self.rect.width

    @property
    def height(self) -> int:
        return self.rect.height

    @property
    def centerx(self) -> int:
        return self.rect.centerx

    @property
    def centery(self) -> int:
        return self.rect.centery


class Camera:

    """
    Class that represents the absolute position of the camera (player)
    in the game world.
    """

    _camera = None

    def __new__(cls, centerx: int = 0, centery: int = 0):
        if cls._camera is None:
            cls._camera = super().__new__(cls)
            cls._camera.screen = Screen()
            cls._camera.x = centerx - cls._camera.screen.centerx
            cls._camera.y = centery - cls._camera.screen.centery

        return cls._camera

    def __str__(self) -> str:
        return f"Camera (x={self.x}, y={self.y}, centerx={self.centerx}, centery={self.centery})"

    @classmethod
    def delete(cls):
        cls._camera = None

    @property
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)

    @position.setter
    def position(self, delta: tuple[int, int]) -> None:
        self.x = round(self.x - delta[0])
        self.y = round(self.y - delta[1])

    @property
    def centerx(self) -> int:
        """Returns the center cornor x position."""
        return self.x + self.screen.centerx

    @property
    def centery(self) -> int:
        """Returns the center cornor y position."""
        return self.y + self.screen.centery

    @property
    def position_center(self) -> tuple[int, int]:
        return (self.centerx, self.centery)

    def get_relative_position(self, x: int, y: int) -> tuple[int, int]:
        """
        Returns the relative position of a coordinate in relation to the
        camera position.
        """
        return (
            round(x - self.x),
            round(x - self.y),
        )
