#!/usr/bin/env python
# coding=utf-8
import multiprocessing
from typing import Optional

import pygame as pg

from pysurvive.player.misc import AnimatedSprite, LowerBodyState, Spritesheet


class PlayerFeets(AnimatedSprite):

    """Player lower body / feets object/sprite."""

    def __init__(self) -> None:
        super().__init__()
        self.movement_state = LowerBodyState.IDLE

        # 256 // 2 = 128
        # x_offset, y_offset = (112, 135)  # already scaled with 2

        spritesheet_paths = []
        for movement in LowerBodyState:
            spritesheet_paths.append(f"player/default/feets/{movement.name.lower()}")
        with multiprocessing.Pool() as pool:
            self.sprites = pool.map(Spritesheet, spritesheet_paths)
        for spritesheet in self.sprites:
            for image in spritesheet:
                image.deserialize()

        # Ensure to set rect first. Otherwise rect is None in image setter.
        self.rect = self.sprite.image.get_frect()
        self.image = self.sprite.image

        # Virtual position the image at the center of the screen.
        # The position of image/rect used for drawing only.
        # self.rect.center = (
        #     x_offset - self.rect.width // 2 + self.group.camera.screenx,
        #     y_offset - self.rect.height // 2 + self.group.camera.screeny,
        # )
        # self.rect.center = (
        #     round(
        #         self.group.player.virt_x
        #         - math.cos(self.group.player.weapon_angle) * self.feet_offset_px
        #         - math.cos(self.group.player.weapon_angle - math.pi / 2)
        #         * self.feet_offset_px
        #         // 2
        #     ),
        #     round(
        #         self.group.player.virt_y
        #         - math.sin(self.group.player.weapon_angle) * self.feet_offset_px
        #         - math.sin(self.group.player.weapon_angle - math.pi / 2)
        #         * self.feet_offset_px
        #         // 2
        #     ),
        # )

    @property
    def x(self) -> float:
        return self.rect.centerx

    @property
    def y(self) -> float:
        return self.rect.centery

    @x.setter
    def x(self, _x: float) -> None:
        self.rect.centerx = _x

    @y.setter
    def y(self, _y: float) -> None:
        self.rect.centery = _y

    @property
    def image(self) -> Optional[pg.surface.Surface]:
        """Overwrite getter of pg.sprite.Sprite."""
        return self.__image

    @image.setter
    def image(self, _image: Optional[pg.surface.Surface]) -> None:
        """Overwrite setter of pg.sprite.Sprite to always center the rect."""
        _rect = _image.get_frect()
        _rect.center = (self.x, self.y)
        self.__image = _image
        self.rect = _rect

    def input(self, direction: pg.math.Vector2):
        self.direction = direction

    def update(self, dt: float, target) -> None:
        """Update the player lower body / feets."""
        super().update(dt)
        self.x = target.x
        self.y = target.y

    def rotate(self, angle: float) -> None:
        self.image = self.sprite.rotate(angle)

    def animate(self) -> None:
        super().animate()
        if self.direction.x == 0 and self.direction.y == 0:
            # Idle state
            self._switch_movement(LowerBodyState.IDLE)
        elif self.direction.x != 0 or self.direction.y != 0:
            # Walk state
            self._switch_movement(LowerBodyState.WALK)
