#!/usr/bin/env python
# coding=utf-8
import math
import os
from enum import Enum, unique
from typing import Generator, Union

import pygame as pg

from pysurvive.config import FPS, IMAGE_DIR
from pysurvive.logger import Logger
from pysurvive.utils import load_image

logger = Logger()


@unique
class DefaultState(Enum):
    IDLE = 0


@unique
class UpperBodyState(Enum):
    IDLE = 0
    MOVE = 1
    # MELEEATTACK = 2
    # SHOOT = 3
    # RELOAD = 4


@unique
class LowerBodyState(Enum):
    IDLE = 0
    WALK = 1
    WALK_LEFT = 2
    WALK_RIGHT = 3
    RUN = 4


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
    )

    def __init__(self, image: pg.surface.Surface) -> None:
        self.image = self._scale(image)
        self.image_buffer = None
        self.rect = self.image.get_rect()
        self.serialize()  # Serialize after pre-processing.

    def serialize(self) -> None:
        """Serializer for multiprocessing purpose."""
        self.image_buffer = pg.image.tostring(self.image, "RGBA")
        del self.image

    def deserialize(self) -> None:
        """Deserializer for multiprocessing purpose."""
        self.image = pg.image.frombuffer(self.image_buffer, self.rect.size, "RGBA")
        del self.image_buffer

    def rotate(self, radian: float) -> pg.surface.Surface:
        """Rotate the surface based on the original one."""
        degree = RotatableImage.angle_to_degree(radian)
        image = pg.transform.rotate(self.image, degree)

        return image

    @staticmethod
    def angle_to_radian(degree: int) -> float:
        """Angle from degree to radian.
        Negative angle amounts will rotate clockwise."""
        return -1 * degree * math.pi / 180

    @staticmethod
    def angle_to_degree(radian: float) -> int:
        """Angle from radian to degree.
        Negative angle amounts will rotate clockwise."""
        return int(-1 * radian * 180 / math.pi)

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
        self._period = 1.5 / FPS

        self.movement_state = DefaultState.IDLE
        self.direction = pg.math.Vector2()
        self.speed = 200

    def _switch_movement(
        self,
        movement_state: Union[
            DefaultState, UpperBodyState, LowerBodyState, WeaponsState
        ],
    ) -> None:
        self.old_movement_state = self.movement_state  # Save old state
        self.movement_state = movement_state
        # Reset frame if movement_state differ.
        if self.old_movement_state != self.movement_state:
            self.frame = 0

    @property
    def sprite(self) -> RotatableImage:
        """Returns the active image object (RotatableImage)
        of the spritesheet (movement)."""
        return self.sprites[self.movement_state.value][self.frame]

    def update(self, dt: float) -> None:
        """Update the player object."""
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
            self.frame %= len(self.sprites[self.movement_state.value])
            # Handle the different images for animation here

    def animate(self) -> None:
        pass


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
