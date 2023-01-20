#!/usr/bin/env python
# coding=utf-8
import math
import os
from enum import Enum, unique
from typing import Generator

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

    __slots__ = (
        "image",
        "image_buffer",
        "rect",
        "rotated_bounding_rects",
    )

    # For example, an accuracy of 10 results in
    # 36 rotated images at 360 degrees.
    rotation_accuracy = 2

    def __init__(self, image: pg.surface.Surface) -> None:
        self.image = self._scale(image)
        self.image_buffer = None
        self.rect = self.image.get_rect()
        self.rotated_bounding_rects: list[pg.rect.Rect] = []

        self._pre_calc_bounding_rects()
        self.serialize()  # Serialize after pre-processing.

    def serialize(self) -> None:
        """Serializer for multiprocessing purpose."""
        self.image_buffer = pg.image.tostring(self.image, "RGBA")
        del self.image

    def deserialize(self) -> None:
        """Deserializer for multiprocessing purpose."""
        self.image = pg.image.frombuffer(self.image_buffer, self.rect.size, "RGBA")
        del self.image_buffer

    def angle_to_radian(self, degree: int) -> float:
        """Angle from degree to radian."""
        return -1 * degree * math.pi / 180

    def angle_to_degree(self, radian: float) -> int:
        """Angle from radian to degree."""
        return int(-1 * radian * 180 / math.pi)

    def rotate(
        self, radian: float, x: int, y: int
    ) -> tuple[pg.surface.Surface, pg.rect.Rect, pg.rect.Rect]:
        """
        Rotate the surface and rect based on the original one.
        Keep the image on the same position.
        """
        degree = self.angle_to_degree(radian)
        image = pg.transform.rotate(self.image, degree)
        rect = image.get_rect()
        # Put the new rect's center at old center.
        rect.center = (x, y)

        # Get the pre-calculated bounding rect and center it.
        bounding_rect = self.rotated_bounding_rects[
            abs(degree) // self.rotation_accuracy
        ].copy()
        bounding_rect.center = (
            x + bounding_rect.centerx - rect.width // 2,
            y + bounding_rect.centery - rect.height // 2,
        )

        return image, rect, bounding_rect

    def _pre_calc_bounding_rects(self) -> None:
        """Pre-rotate the image within a range of angles."""
        for degree in range(0, 360, self.rotation_accuracy):
            # Negative angle amounts will rotate clockwise.
            image = pg.transform.rotate(self.image, -1 * degree)
            self.rotated_bounding_rects.append(image.get_bounding_rect())

    @staticmethod
    def _scale(image: pg.surface.Surface, scale: int = 2) -> pg.surface.Surface:
        """Scaling image down."""
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

    __slots__ = (
        "sprite_size",
        "spritesheet_path",
        "sprites",
    )

    spritesheet_name = "spritesheet.png"

    def __init__(self, spritesheet_path: str, sprite_size: int = 512) -> None:
        self.sprite_size = sprite_size
        self.spritesheet_path = f"{IMAGE_DIR}/{spritesheet_path}"
        self.sprites: list[RotatableImage] = []
        self._load_sprites()

    def __repr__(self) -> str:
        return f"Spritesheet<{self.spritesheet_path}>"

    def __iter__(self) -> Generator[RotatableImage, None, None]:
        for sprite in self.sprites:
            yield sprite

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
