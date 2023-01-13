#!/usr/bin/env python
# coding=utf-8
import pygame as pg

from pysurvive.config import SCREEN_RECT


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        print(cls._instances[cls])
        return cls._instances[cls]


class Screen(pg.rect.Rect, metaclass=Singleton):

    """
    Class that represent the screen and is used to detect
    wheather objects are visible on the screen.
    """

    def __str__(self) -> str:
        return f"Screen (size={self.width}x{self.height})"

    @classmethod
    def delete(cls) -> None:
        """Unset singleton."""
        cls._instances = {}

    @property
    def rect(self) -> pg.rect.Rect:
        """The function spritecollide expects a property rect."""
        return self


class Camera(metaclass=Singleton):

    """
    Class that represents the absolute position of the
    camera (player) in the game world.
    """

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.screen = Screen(SCREEN_RECT)
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"Camera (x={self.x}, y={self.y})"

    @classmethod
    def delete(cls) -> None:
        """Unset singleton."""
        cls._instances = {}

    @property
    def position(self) -> tuple[int, int]:
        """Returns camera position in a tuple."""
        return (self.x, self.y)

    def move(self, delta: tuple[int, int]) -> None:
        """Move the camera by delta x, y."""
        self.x = round(self.x - delta[0])
        self.y = round(self.y - delta[1])

    def get_relative_position(self, x: int, y: int) -> tuple[int, int]:
        """
        Returns the relative position of a coordinate in relation
        to the global camera position in the center of the screen.
        """
        return (
            round(x - self.x + self.screen.centerx),
            round(y - self.y + self.screen.centery),
        )
