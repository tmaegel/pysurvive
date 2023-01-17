#!/usr/bin/env python
# coding=utf-8
import math
import os
from enum import Enum, unique

import pygame as pg

from pysurvive.config import FPS, IMAGE_DIR
from pysurvive.logger import Logger
from pysurvive.utils import load_image

logger = Logger()


@unique
class MovementState(Enum):
    IDLE = 0
    MOVE = 1
    # MELEEATTACK = 2
    # SHOOT = 3
    # RELOAD = 4


@unique
class WeaponsState(Enum):
    KNIFE = 0
    HANDGUN = 1
    RIFLE = 2
    SHOTGUN = 3


class RotatableImage:

    """Represents a single image of a spritesheet."""

    def __init__(self, image: pg.surface.Surface) -> None:
        self.image = self._scale(image)

    def rotate(
        self, x: int, y: int, angle: float
    ) -> tuple[pg.surface.Surface, pg.rect.Rect]:
        """
        R the surfaces and rect based on the original one.
        Keep the image on the same position.
        """
        image = pg.transform.rotate(
            self.image,
            (-1 * angle * 180 / math.pi),
        )
        rect = image.get_rect()
        # Put the new rect's center at old center.
        rect.center = (x, y)

        return image, rect

    @staticmethod
    def _scale(image: pg.surface.Surface, scale: int = 2) -> pg.surface.Surface:
        """scaling image down."""
        # pg.transform.scale
        return pg.transform.smoothscale(
            image,
            (
                image.get_rect().width // scale,
                image.get_rect().height // scale,
            ),
        )


class AnimatedSprite(pg.sprite.Sprite):

    """Base class for complex animated sprite objects."""

    def __init__(self) -> None:
        super().__init__()
        # Contains a list of spritesheets for each movement/state.
        self.sprites: list[Spritesheet] = []
        # Current image of the animation sequence/images.
        self.frame = 0
        # Next time it has to be updated in ms.
        self._next_update = 0
        # Frequency/period of the animation in ms.
        self._period = 1500.0 / FPS
        self.speed = 7
        self.direction = (0, 0)
        self.movement_state = MovementState.IDLE
        self.old_movement_state = self.movement_state

    @property
    def sprite(self) -> RotatableImage:
        """
        Returns the active image object (RotatableImage)
        of the spritesheet (movement).
        """
        return self.sprites[self.movement_state.value][self.frame]

    @property
    def move_vector(self) -> tuple[float, float]:
        """
        If the object moves diagonal add only the half of the speed
        in each direction.
        """
        if self.direction[0] != 0 and self.direction[1] != 0:
            # Based on the 45° angle
            return (
                -1 * self.direction[0] * abs(math.cos(math.pi / 4)) * self.speed,
                -1 * self.direction[1] * abs(math.sin(math.pi / 4)) * self.speed,
            )
        return (
            -1 * self.direction[0] * self.speed,
            -1 * self.direction[1] * self.speed,
        )

    def _switch_movement(self, movement_state: MovementState) -> None:
        self.old_movement_state = self.movement_state  # Save old state
        self.movement_state = movement_state
        # Reset frame if movement_state differ.
        if self.old_movement_state != self.movement_state:
            self.frame = 0


class Spritesheet:

    """
    A collection of sprites of a movement (e.g. idle, move).
    Sprites of an spritesheet are referenced by an index which
    is defined by the frame.
    """

    spritesheet_name = "spritesheet.png"

    def __init__(self, spritesheet_path: str, sprite_size: int = 512) -> None:
        self.sprite_size = sprite_size
        self.spritesheet_path = f"{IMAGE_DIR}/{spritesheet_path}"
        self.sprites: list[RotatableImage] = []
        self._load_sprites()

    def __len__(self) -> int:
        return len(self.sprites)

    def __getitem__(self, frame: int) -> RotatableImage:
        return self.sprites[frame]

    def _load_sprites(self) -> None:
        """Preloading sprites from the spritesheet."""
        if not os.path.isdir(self.spritesheet_path):
            logger.warning("Directory %s doesnt exists.", self.spritesheet_path)
            return
        logger.info("Loading spritesheet from path %s.", self.spritesheet_path)
        self.sprites = self._split_spritesheet(
            f"{self.spritesheet_path}/{self.spritesheet_name}"
        )

    def _split_spritesheet(self, spritesheet_file: str) -> list[RotatableImage]:
        """Cut the individual sprites from the spritesheet."""
        spritesheet, _ = load_image(spritesheet_file, alpha=True)
        spritesheet_width, _ = spritesheet.get_size()
        sprites: list[RotatableImage] = []
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
