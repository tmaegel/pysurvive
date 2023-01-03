#!/usr/bin/env python
# coding=utf-8
import math
import os
from enum import Enum, unique

import pygame as pg

from pysurvive.config import IMAGE_DIR
from pysurvive.logger import Logger
from pysurvive.utils import load_image

logger = Logger()


@unique
class MovementState(Enum):
    IDLE = 0
    MOVE = 1
    MELEEATTACK = 2
    SHOOT = 3
    RELOAD = 4


@unique
class WeaponsState(Enum):
    KNIFE = 0
    HANDGUN = 1
    RIFLE = 2
    SHOTGUN = 3


class RotatableImage:
    def __init__(self, image: pg.Surface) -> None:
        self.image = self._scale(image)

    @staticmethod
    def _scale(image: pg.Surface, scale: int = 2) -> pg.Surface:
        """Scaling image down."""
        # pg.transform.scale
        return pg.transform.smoothscale(
            image,
            (
                image.get_rect().width // scale,
                image.get_rect().height // scale,
            ),
        )

    def rotate(self, angle: int) -> pg.Surface:
        """Return rotated surfaces based on the original one."""
        return pg.transform.rotate(
            self.image,
            (-1 * angle * (180 / math.pi)),
        )


class PlayerSpritesheet:
    def __init__(self, custom_path: str) -> None:
        self.sprite_size = 512
        self.spritesheet_name = "spritesheet.png"
        self.root_path = f"{IMAGE_DIR}/player/{custom_path}"
        self.images: list[list[RotatableImage]] = []
        self._load_images()

    def __len__(self) -> int:
        return len(self.images)

    def __getitem__(self, frame: int) -> list[RotatableImage]:
        return self.images[frame]

    def _load_images(self) -> None:
        """Preloading images for each movement state from spritesheet."""
        for movement in MovementState:
            path = f"{self.root_path}/{movement.name.lower()}"
            if not os.path.isdir(path):
                logger.warning("Directory %s doesnt exists.", directory)
                continue
            logger.info("Loading spritesheet from path %s.", path)
            self.images.append(
                self._split_spritesheet(f"{path}/{self.spritesheet_name}")
            )

    def _split_spritesheet(self, spritesheet_file: str) -> list[pg.Surface]:
        """Cut the individual sprites from the spritesheet."""
        spritesheet, _ = load_image(spritesheet_file, alpha=True)
        spritesheet_width, _ = spritesheet.get_size()
        sprites: list[pg.Surface] = []
        for sprite_x in range(0, spritesheet_width // self.sprite_size):
            rect = (
                sprite_x * self.sprite_size,
                0,
                self.sprite_size,
                self.sprite_size,
            )
            # Subsurface doesn’t create copies in memory.
            sprite = spritesheet.subsurface(rect)
            sprites.append(RotatableImage(sprite))

        return sprites
