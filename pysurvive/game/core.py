#!/usr/bin/env python
# coding=utf-8
import pygame as pg

from pysurvive.config import SCREEN_RECT


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


class Screen(pg.rect.Rect, metaclass=Singleton):

    """
    Class that represent the screen and is used to detect
    wheather objects are visible on the screen.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Calculate a slightly larger rectangle of the screen.
        # Otherwise, there will be white flickering at the edges
        # when drawing the sprites on the screen.
        rough_w = self.width * 0.01
        rough_h = self.height * 0.01
        self.rect_rough = pg.Rect(
            self.x - rough_w,
            self.y - rough_w,
            self.width + rough_w * 2,
            self.height + rough_h * 2,
        )

    def __str__(self) -> str:
        return f"Screen (size={self.width}x{self.height})"

    @classmethod
    def delete(cls) -> None:
        """Unset singleton."""
        cls._instances = {}

    @property
    def rect(self) -> pg.rect.Rect:
        """
        The function spritecollide expects a property rect.
        Returns the rough rect of the screen here.
        """
        return self.rect_rough


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

    def get_rel_position(self, x: int, y: int) -> tuple[int, int]:
        """
        Returns the relative position of a coordinate in relation
        to the global camera position in the center of the screen.
        """
        return (
            round(x - self.x + self.screen.centerx),
            round(y - self.y + self.screen.centery),
        )
