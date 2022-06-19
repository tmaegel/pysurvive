#!/usr/bin/env python
# coding=utf-8
import math

import pygame as pg

# from pysurvive.class_toolchain import Ray
from pysurvive.config import COLORKEY, GRAY_LIGHT, RED


class Bullet(pg.sprite.Sprite):

    """Represents the bullets (shooting) of the player."""

    trail_offset = 25

    def __init__(self, _x, _y, _angle):
        # super().__init__(_x, _y, _angle)
        super().__init__()
        self.x = _x
        self.y = _y
        self.angle = _angle
        self.size = 10
        self.image = pg.Surface((self.size, self.size))
        self.image.fill(RED)
        self.image.set_colorkey(COLORKEY)
        self.rect = pg.Rect(self.x, self.y, self.size, self.size)
        # self._render()
        # Draw the impact position if true. Otherwise draw the trail of the bullet.
        # self.impact = False

    def update(self, dt: int = None, direction: tuple[int, int] = None) -> None:
        """Update the bullet position."""
        pass

    def _render(self) -> None:
        pass

    # def draw(self, screen, offset):
    #     """
    #     Draw the bullet.
    #     """
    #
    #     if self.intersect:
    #         if self.impact:
    #             # Draw the impact
    #             pg.draw.circle(
    #                 screen,
    #                 (255, 0, 0),
    #                 (self.intersect["x"] - offset[0], self.intersect["y"] - offset[1]),
    #                 2,
    #             )
    #         else:
    #             # Draw the trail of the bullet
    #             pg.draw.line(
    #                 screen,
    #                 GRAY_LIGHT,
    #                 (
    #                     self.x0 - offset[0] + math.cos(self.angle) * self.trail_offset,
    #                     self.y0 - offset[1] + math.sin(self.angle) * self.trail_offset,
    #                 ),
    #                 (self.intersect["x"] - offset[0], self.intersect["y"] - offset[1]),
    #             )
    #             self.impact = True
