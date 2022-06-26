#!/usr/bin/env python
# coding=utf-8
import math
import random

import pygame as pg


class MapObject(pg.sprite.Sprite):
    def __init__(
        self, _x: int, _y: int, _image: pg.Surface, rotation: bool = False
    ) -> None:
        super().__init__()
        self.image = _image
        if rotation:
            self.image = self.init_rotation(random.randint(0, 360))
        self.rect = self.image.get_rect()
        self.x = _x
        self.y = _y
        self.rect.x = self.x
        self.rect.y = self.y

    def init_rotation(self, angle: int) -> pg.Surface:
        """Return rotated surfaces based on the original one."""
        return pg.transform.rotate(
            self.image,
            (-1 * angle * (180 / math.pi)),
        )
