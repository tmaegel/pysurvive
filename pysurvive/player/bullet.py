#!/usr/bin/env python
# coding=utf-8
import math

import pygame as pg

from pysurvive.class_toolchain import Ray
from pysurvive.config import GRAY_LIGHT


class Bullet(Ray):

    # Draw the impact position if true.
    # Otherwise draw the trail of the bullet.
    impact = False

    trail_offset = 25

    def __init__(self, _x, _y, _angle):
        Ray.__init__(self, _x, _y, _angle)

    def draw(self, screen, offset):
        """
        Draw the bullet.
        """

        if self.intersect:
            if self.impact:
                # Draw the impact
                pg.draw.circle(
                    screen,
                    (255, 0, 0),
                    (self.intersect["x"] - offset[0], self.intersect["y"] - offset[1]),
                    2,
                )
            else:
                # Draw the trail of the bullet
                pg.draw.line(
                    screen,
                    GRAY_LIGHT,
                    (
                        self.x0 - offset[0] + math.cos(self.angle) * self.trail_offset,
                        self.y0 - offset[1] + math.sin(self.angle) * self.trail_offset,
                    ),
                    (self.intersect["x"] - offset[0], self.intersect["y"] - offset[1]),
                )
                self.impact = True
