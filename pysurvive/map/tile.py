#!/usr/bin/env python
# coding=utf-8
import pygame as pg

from pysurvive.config import DEBUG_SPRITE, RED
from pysurvive.game.core import Camera


class Tile(pg.sprite.Sprite):

    """Single tile object."""

    __slots__ = (
        "camera",
        "image",
        "rect",
        "bounding_rect",
        "x",
        "y",
        "enter",
        "block",
    )

    def __init__(
        self,
        image: pg.surface.Surface,
        bounding_rect: pg.Rect,
        x: int = 0,
        y: int = 0,
        enter: bool = False,
        block: bool = False,
    ) -> None:
        super().__init__()
        self.camera = Camera()

        # Real position in the game world.
        # Should never change for static objects.
        self.x = x
        self.y = y

        self.image = image
        self.rect = self.image.get_rect()
        self.bounding_rect = bounding_rect

        # Tile properties.
        self.enter = enter
        self.block = block

        if DEBUG_SPRITE:
            self._render_debug()

    def __str__(self) -> str:
        return f"Tile({self.x}, {self.y}, {self.width}, {self.height})"

    def __deepcopy__(self, _):
        """Create a deep copy of this object."""
        return Tile(
            image=self.image,
            bounding_rect=self.bounding_rect,
            x=self.rect.x,
            y=self.rect.y,
            enter=self.enter,
            block=self.block,
        )

    def _render_debug(self) -> None:
        """Render additional debug content (e.g. border) on the sprite image."""
        if not self.enter:
            pg.draw.rect(
                self.image,
                RED,
                self.bounding_rect,
                width=1,
            )

    @property
    def rel_x(self) -> int:
        """Get the x coordinate of the tile relative to the camera."""
        return self.rect.x

    @rel_x.setter
    def rel_x(self, x: int) -> None:
        """Set the x coordinate of the tile relative to the camera."""
        self.rect.x = x

    @property
    def rel_y(self) -> int:
        """Get the y coordinate of the tile relative to the camera."""
        return self.rect.y

    @rel_y.setter
    def rel_y(self, y: int) -> None:
        """Set the y coordinate of the tile relative to the camera."""
        self.rect.y = y

    @property
    def width(self) -> int:
        """Returns the width of the tile."""
        return self.rect.width

    @property
    def height(self) -> int:
        """Returns the height of the tile."""
        return self.rect.height

    def update(self) -> None:
        """Update the relative position of the tile object in relation
        to the global camera position (center of the screen)."""
        self.rel_x, self.rel_y = self.camera.get_rel_position(self.x, self.y)


class TileGroup(pg.sprite.RenderPlain):
    def __init__(self):
        super().__init__()

    # def draw() -> None:
    # @todo: Draw red border for close tiles
    # pass

    # def close_tiles(self) -> list[Tile]:
    #     pass
