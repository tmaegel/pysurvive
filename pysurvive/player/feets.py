#!/usr/bin/env python
# coding=utf-8
import multiprocessing
from typing import Optional

import pygame as pg

from pysurvive.player.misc import (
    AnimatedSprite,
    LowerBodyState,
    RotatableImage,
    Spritesheet,
)


class PlayerFeets(AnimatedSprite):

    """Player lower body / feets object/sprite."""

    def __init__(self) -> None:
        super().__init__()
        self.movement_state = LowerBodyState.IDLE

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

    def animate(self, angle: float) -> None:
        super().animate()
        if self.direction.x == 0 and self.direction.y == 0:
            # Idle state
            self._switch_movement(LowerBodyState.IDLE)
        elif self.direction.x != 0 and self.direction.y != 0:
            # Walk state (on diagonal axis)
            degree = abs(RotatableImage.angle_to_degree(angle))
            if degree >= 0 and degree < 90:
                if (
                    self.direction.x > 0
                    and self.direction.y > 0
                    or self.direction.x < 0
                    and self.direction.y < 0
                ):
                    self._switch_movement(LowerBodyState.WALK)
                else:
                    if self.direction.y < 0:
                        self._switch_movement(LowerBodyState.WALK_LEFT)
                    else:
                        self._switch_movement(LowerBodyState.WALK_RIGHT)
            elif degree >= 90 and degree < 180:
                if (
                    self.direction.x < 0
                    and self.direction.y > 0
                    or self.direction.x > 0
                    and self.direction.y < 0
                ):
                    self._switch_movement(LowerBodyState.WALK)
                else:
                    if self.direction.y < 0:
                        self._switch_movement(LowerBodyState.WALK_RIGHT)
                    else:
                        self._switch_movement(LowerBodyState.WALK_LEFT)
            elif degree >= 180 and degree < 270:
                if (
                    self.direction.x < 0
                    and self.direction.y < 0
                    or self.direction.x > 0
                    and self.direction.y > 0
                ):
                    self._switch_movement(LowerBodyState.WALK)
                else:
                    if self.direction.y < 0:
                        self._switch_movement(LowerBodyState.WALK_RIGHT)
                    else:
                        self._switch_movement(LowerBodyState.WALK_LEFT)
            elif degree >= 270 and degree < 360:
                if (
                    self.direction.x > 0
                    and self.direction.y < 0
                    or self.direction.x < 0
                    and self.direction.y > 0
                ):
                    self._switch_movement(LowerBodyState.WALK)
                else:
                    if self.direction.y < 0:
                        self._switch_movement(LowerBodyState.WALK_LEFT)
                    else:
                        self._switch_movement(LowerBodyState.WALK_RIGHT)
        elif self.direction.x != 0 or self.direction.y != 0:
            # Walk state (on axis)
            degree = abs(RotatableImage.angle_to_degree(angle))
            if degree > 315 and degree <= 360 or degree >= 0 and degree <= 45:
                if self.direction.y == 0:
                    # Walk on x-axis only.
                    self._switch_movement(LowerBodyState.WALK)
                else:
                    if self.direction.y < 0:
                        self._switch_movement(LowerBodyState.WALK_LEFT)
                    else:
                        self._switch_movement(LowerBodyState.WALK_RIGHT)
            elif degree > 45 and degree <= 135:
                if self.direction.x == 0:
                    # Walk on y-axis only.
                    self._switch_movement(LowerBodyState.WALK)
                else:
                    if self.direction.x < 0:
                        self._switch_movement(LowerBodyState.WALK_RIGHT)
                    else:
                        self._switch_movement(LowerBodyState.WALK_LEFT)
            elif degree > 135 and degree <= 225:
                if self.direction.y == 0:
                    # Walk on x-axis only.
                    self._switch_movement(LowerBodyState.WALK)
                else:
                    if self.direction.y < 0:
                        self._switch_movement(LowerBodyState.WALK_RIGHT)
                    else:
                        self._switch_movement(LowerBodyState.WALK_LEFT)
            elif degree > 225 and degree <= 315:
                if self.direction.x == 0:
                    # Walk on y-axis only.
                    self._switch_movement(LowerBodyState.WALK)
                else:
                    if self.direction.x < 0:
                        self._switch_movement(LowerBodyState.WALK_LEFT)
                    else:
                        self._switch_movement(LowerBodyState.WALK_RIGHT)
