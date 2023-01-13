#!/usr/bin/env python
# coding=utf-8
import pygame as pg

from pysurvive.config import DEBUG_SPRITE, RED
from pysurvive.game.core import Camera


class Tile(pg.sprite.Sprite):

    """Single tile object."""

    def __init__(
        self,
        tile_image: pg.surface.Surface,
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

        self.image = tile_image
        self.rect = self.image.get_rect()

        # Tile properties.
        self.enter = enter
        self.block = block

        self._render()

    def __deepcopy__(self, memo):
        """Create a deep copy of this object."""
        return Tile(self.image, self.rect.x, self.rect.y, self.enter, self.block)

    @property
    def rel_x(self) -> int:
        """Get the relative x coordinate of the tile on the screen."""
        return self.rect.x

    @rel_x.setter
    def rel_x(self, x: int) -> None:
        """Set the relative x coordinate of the tile on the screen."""
        self.rect.x = x

    @property
    def rel_y(self) -> int:
        """Get the rel y coordinate of the tile on the screen."""
        return self.rect.y

    @rel_y.setter
    def rel_y(self, y: int) -> None:
        """Set the rel y coordinate of the tile on the screen."""
        self.rect.y = y

    def _render(self) -> None:
        """Render additional content on the sprite image."""
        # Draw debug border
        if DEBUG_SPRITE and not self.enter:
            pg.draw.rect(
                self.image,
                RED,
                pg.Rect(
                    0,
                    0,
                    self.rect.width,
                    self.rect.height,
                ),
                width=1,
            )

    def update(self) -> None:
        """
        Update the tile object position relative
        to the camera position.
        """
        self.rel_x, self.rel_y = self.camera.get_relative_position(self.x, self.y)
