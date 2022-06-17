#!/usr/bin/env python
# coding=utf-8
import math
import os

import pygame as pg

from pysurvive.class_toolchain import Animation
from pysurvive.config import IMAGE_DIR
from pysurvive.logger import logger
from pysurvive.utils import load_image


class PlayerFeet(Animation):

    """
    A player subclass to hold the feet images / states of the player.
    """

    scale = 5

    # @workaroung: offset (20) for rifle, shutgun and knife
    feet_offset_px = 5

    feet_index = 0
    feets = [
        "idle",
        "walk",
        "walk_left",
        "walk_right",
        "run",
    ]

    def __init__(self, _player):
        Animation.__init__(self)
        self.player = _player

        for feet in self.feets:
            _images = []
            directory = IMAGE_DIR + "player/feet/" + feet + "/"
            if os.path.isdir(directory):
                path, _, files = next(os.walk(directory))
                for img in sorted(files):
                    if "spritesheet" not in img:
                        image, _ = load_image(path + img, alpha=True, path=False)
                        _images.append(
                            pg.transform.scale(
                                image,
                                (
                                    image.get_rect().width // self.scale,
                                    image.get_rect().height // self.scale,
                                ),
                            )
                        )
                self.images.append(_images)
            else:
                logger.warning("Directory %s doesnt exists.", directory)

        self.image = self.images[self.feet_index][self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = (
            round(
                self.player.get_virt_x()
                - math.cos(self.player.get_weapon_angle()) * self.feet_offset_px
                - math.cos(self.player.get_weapon_angle() - math.pi / 2)
                * self.feet_offset_px
                // 2
            ),
            round(
                self.player.get_virt_y()
                - math.sin(self.player.get_weapon_angle()) * self.feet_offset_px
                - math.sin(self.player.get_weapon_angle() - math.pi / 2)
                * self.feet_offset_px
                // 2
            ),
        )

    def update(self, dt, direction):
        """
        Update the player feets object.
        """

        # Accumulate time since last update.
        self._next_update += dt
        # If more time has passed as a period, then we need to update.
        if self._next_update >= self._period:
            # Skipping frames if too much time has passed.
            # Since _next_update is bigger than period this is at least 1.
            self.frame += int(self._next_update / self._period)
            # Time that already has passed since last update.
            self._next_update %= self._period
            # Limit the frame to the length of the image list.
            self.frame %= len(self.images[self.feet_index])

        # @todo: Not time based yet
        self.move(direction)
        self.rotate()

    def move(self, direction):
        """
        Move the player feets in the specific direction.
        """

        self.rect.center = (self.player.get_virt_x(), self.player.get_virt_y())
        self.rect.center = (
            round(
                self.player.get_virt_x()
                - math.cos(self.player.get_weapon_angle()) * self.feet_offset_px
                - math.cos(self.player.get_weapon_angle() - math.pi / 2)
                * self.feet_offset_px
                // 2
            ),
            round(
                self.player.get_virt_y()
                - math.sin(self.player.get_weapon_angle()) * self.feet_offset_px
                - math.sin(self.player.get_weapon_angle() - math.pi / 2)
                * self.feet_offset_px
                // 2
            ),
        )

        self.rect.move_ip(*[d * self.player.speed for d in direction])

        if direction[0] != 0 or direction[1] != 0:
            # Move state
            self.feet_index = 1
        elif direction[0] == 0 and direction[1] == 0:
            # Idle state
            self.frame = 0
            self.feet_index = 0

    def rotate(self) -> None:
        """
        Rotate the player feets object on the center.
        Need to negate the result, if the image starts
        at the wrong direction.
        """

        # Need to negate the result, if the image starts
        # at the wrong direction.
        self.image = pg.transform.rotate(
            self.images[self.feet_index][self.frame],
            (-1 * self.player.get_weapon_angle() * (180 / math.pi)),
        )
        # Keep the image on the same position.
        # Save its current center.
        x, y = self.rect.center
        # Replace old rect with new rect.
        self.rect = self.image.get_rect()
        # Put the new rect's center at old center.
        self.rect.center = (x, y)
