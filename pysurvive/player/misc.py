#!/usr/bin/env python
# coding=utf-8
import math
import os
from enum import Enum, unique

import pygame as pg

from pysurvive.config import IMAGE_DIR
from pysurvive.logger import logger
from pysurvive.utils import load_image


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
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self._load_image(self.filename)
        self._scale_image()

    def _load_image(self, filename: str) -> None:
        """Load image from filesystem."""
        logger.debug("Loading image from file %s.", filename)
        self.image, _ = load_image(filename, alpha=True, path=False)

    def _scale_image(self, scale: int = 4) -> None:
        """Scaling image down."""
        self.image = pg.transform.scale(
            self.image,
            (
                self.image.get_rect().width // scale,
                self.image.get_rect().height // scale,
            ),
        )

    def rotate(self, angle: int) -> pg.Surface:
        """Return rotated surfaces based on the original one."""
        return pg.transform.rotate(
            self.image,
            (-1 * angle * (180 / math.pi)),
        )


class PlayerImages:
    def __init__(self) -> None:
        self.images: list[list[RotatableImage]] = []
        self._load_images()

    def __getitem__(self, frame: int) -> list[RotatableImage]:
        return self.images[frame]

    def _load_images(self) -> None:
        """Preloading images for each movement state."""
        # @todo: Loading other weapon-movement images too.
        for movement in MovementState:
            _images = []
            directory = (
                f"{IMAGE_DIR}/player/"
                + f"{WeaponsState.HANDGUN.name.lower()}/{movement.name.lower()}/"
            )
            if os.path.isdir(directory):
                path, _, files = next(os.walk(directory))
                logger.info("Loading images from path %s.", path)
                for img in sorted(files):
                    if "spritesheet" not in img:
                        _images.append(RotatableImage(f"{path}/{img}"))
                self.images.append(_images)
            else:
                logger.warning("Directory %s doesnt exists.", directory)
