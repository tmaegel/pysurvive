#!/usr/bin/env python
# coding=utf-8

import pygame as pg

from pysurvive.config import DEBUG_SPRITE, GREEN, RED, YELLOW
from pysurvive.game.core import Camera


class Tile(pg.sprite.Sprite):

    """Single tile object."""

    __slots__ = (
        "image",
        "rect",
        "bounding_rect",
        "abs_rect",
        "abs_bounding_rect",
        "offset_x",
        "offset_y",
        "enter",
        "block",
    )

    def __init__(
        self,
        image: pg.surface.Surface,
        x: float = 0,
        y: float = 0,
        enter: bool = False,
        block: bool = False,
    ) -> None:
        super().__init__()
        self.image = image

        self.rect = self.image.get_frect()
        self.bounding_rect = pg.FRect(self.image.get_bounding_rect())
        # The initial x, y of the bounding_rect are the offsets for the bounding rect.
        self.bounding_rect_offset_x = self.bounding_rect.x
        self.bounding_rect_offset_y = self.bounding_rect.y

        # Tile properties.
        self.enter = enter
        self.block = block

    def __repr__(self) -> str:
        return f"Tile({self.x}, {self.y}, {self.width}, {self.height})"

    def __deepcopy__(self, _):
        """Create a deep copy of this object."""
        return Tile(
            image=self.image,
            x=self.x,
            y=self.y,
            enter=self.enter,
            block=self.block,
        )

    @property
    def x(self) -> float:
        return self.rect.x

    @property
    def y(self) -> float:
        return self.rect.y

    @x.setter
    def x(self, _x: float) -> None:
        self.rect.x = _x
        self.bounding_rect.x = self.x + self.bounding_rect_offset_x

    @y.setter
    def y(self, _y: float) -> None:
        self.rect.y = _y
        self.bounding_rect.y = self.y + self.bounding_rect_offset_y

    @property
    def width(self) -> float:
        return self.rect.width

    @property
    def height(self) -> float:
        return self.rect.height

    def debug_draw(
        self,
        surface: pg.surface.Surface,
        offset: pg.Vector2,
        color: pg.Color,
        draw=True,
    ):
        if draw:
            rect = self.bounding_rect.copy()
            rect.x = offset.x + self.bounding_rect_offset_x
            rect.y = offset.y + self.bounding_rect_offset_y
            pg.draw.rect(surface, color, rect, width=1)


class TileGroup(pg.sprite.Group):
    def __init__(self):
        super().__init__()

    def draw(self, surface: pg.surface.Surface, camera: Camera) -> None:
        """Custom variant of the builtin method draw()."""
        for sprite in self.sprites():
            offset = sprite.rect.topleft - camera.offset
            surface.blit(sprite.image, offset)

            # Drawing bounding_rect (border) for debugging.
            # if DEBUG_SPRITE:
            #     sprite.debug_draw(surface, offset, RED, not sprite.enter)


class TileGroupManager:
    def __init__(self):
        # Fix collection of tiles.
        self.tiles_all = TileGroup()
        self.tiles_movement_collision = TileGroup()
        self.tiles_bullet_collision = TileGroup()
        # Variable collection of tiles.
        self.tiles_on_screen = TileGroup()
        self.tiles_close_to_player = TileGroup()
        self.tiles_movement_collision_on_screen = TileGroup()

    def update(self, camera: Camera) -> None:
        """Update the tile groups."""
        # Update tiles on camera/screen.
        self.tiles_on_screen.empty()
        self.tiles_on_screen.add(
            pg.sprite.spritecollide(camera, self.tiles_all, False),
        )

        # Update tiles on screen that are relevant for collision detection.
        self.tiles_movement_collision_on_screen.empty()
        for sprite in self.tiles_movement_collision.sprites():
            if sprite in self.tiles_on_screen.sprites():
                self.tiles_movement_collision_on_screen.add(sprite)

        # Update tiles close to camera.
        self.tiles_close_to_player.empty()
        self.tiles_close_to_player.add(
            camera.near_area_rect.collideobjectsall(self.tiles_on_screen.sprites())
        )

        self.tiles_all.update(camera)  # Update all tiles on the camera/screen.

    def draw(self, surface: pg.surface.Surface, camera: Camera) -> None:
        """Draw tiles visible on camera/screen only."""
        self.tiles_on_screen.draw(surface, camera)

        if DEBUG_SPRITE:
            # Drawing bounding_rect (border) for debugging.
            for sprite in self.tiles_movement_collision_on_screen:
                offset = sprite.rect.topleft - camera.offset
                sprite.debug_draw(surface, offset, GREEN, True)
            for sprite in self.tiles_close_to_player:
                offset = sprite.rect.topleft - camera.offset
                sprite.debug_draw(surface, offset, YELLOW, True)

    def add(self, tile: Tile):
        """Add tiles to the corresponding tile groups."""
        self.tiles_all.add(tile)
        if not tile.enter:
            self.tiles_movement_collision.add(tile)
        if tile.block:
            self.tiles_bullet_collision.add(tile)

    # def close(self, rect: pg.Rect) -> list[Tile]:
    #     """Returns a list of tile objects that collide with the given rect."""
    #     return rect.collideobjectsall(self.tiles_on_screen.sprites())
    #
    # def closes_sprites_movement_collision(self, rect: pg.Rect) -> list[Tile]:
    #     """Returns a list of tile objects that collide with the given rect
    #     and are relevant for movement collision detection."""
    #     return rect.collideobjectsall(self.close_sprites(rect))
