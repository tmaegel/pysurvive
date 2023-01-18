#!/usr/bin/env python
# coding=utf-8
import math
from functools import cached_property

import pygame as pg

from pysurvive.config import DEBUG_SPRITE, GREEN, SOUND_DIR
from pysurvive.game.core import Camera, Screen
from pysurvive.map.level import Level
from pysurvive.map.tile import Tile
from pysurvive.player.misc import (
    AnimatedSprite,
    MovementState,
    Spritesheet,
    WeaponsState,
)
from pysurvive.player.viewpoint import Viewpoint
from pysurvive.utils import load_sound


class PlayerGroup(pg.sprite.RenderPlain):

    """Sprite group that contains all drawable player sprites."""

    def __init__(self, _level: Level) -> None:
        super().__init__()
        self.level = _level  # Reference to the level object.
        self.screen = Screen()
        self.camera = Camera()
        self.viewpoint = Viewpoint()
        self.player = Player(self)
        self.add(
            (
                self.viewpoint,
                self.player,
            )
        )

    def draw(self, surface: pg.surface.Surface) -> list[pg.rect.Rect]:
        """
        Overwrite orginal draw method of RenderPlain.
        """
        sprites = self.sprites()
        if hasattr(surface, "blits"):
            self.spritedict.update(
                zip(sprites, surface.blits((spr.image, spr.rect) for spr in sprites))
            )
        else:
            for spr in sprites:
                self.spritedict[spr] = surface.blit(spr.image, spr.rect)

        if DEBUG_SPRITE:
            for spr in sprites:
                spr.draw_border(surface, spr)

        self.lostsprites = []
        dirty = self.lostsprites

        return dirty


class Player(AnimatedSprite):

    """Player object/sprite."""

    def __init__(self, _group) -> None:
        super().__init__()
        self.group = _group  # Reference to the group with other player object.
        self.weapon_state = WeaponsState.HANDGUN

        # Contains the original (scaled only) images of the player.
        for movement in MovementState:
            # @todo: Loading multiple weapons sprites.
            for weapon in (self.weapon_state,):
                sprites = Spritesheet(
                    f"player/default/{weapon.name.lower()}/{movement.name.lower()}"
                )
                self.sprites.append(sprites)

        # Initialize sprite image.
        self.image = self.sprite.image
        # Rect acts as the virtual position (center of the screen).
        self.rect = self.sprite.rect
        # Virtual position the image at the center of the screen.
        # The position of image/rect used for drawing only.
        self.rect.center = (self.group.screen.centerx, self.group.screen.centery)
        # Initialize the bounding rect.
        self.bounding_rect = self.image.get_bounding_rect()

        # Preloading sounds.
        self.sound_shot = load_sound(f"{SOUND_DIR}/shot/pistol.wav")
        self.sound_reload = load_sound(f"{SOUND_DIR}/reload/pistol.wav")

    @property
    def x(self) -> int:
        """Returns the absolute x coordinate of the player."""
        return self.group.camera.x

    @property
    def y(self) -> int:
        """Returns the absolute y coordinate of the player."""
        return self.group.camera.y

    @property
    def virt_pos(self) -> tuple[int, int]:
        """Get the virtual position (rect) of the player on the screen."""
        return self.rect.center

    @property
    def virt_x(self) -> int:
        """Get the virtual x coordinate (rect) of the player on the screen."""
        return self.rect.centerx

    @property
    def virt_y(self) -> int:
        """Get the virtual y coordinate (rect) of the player on the screen."""
        return self.rect.centery

    @property
    def angle(self) -> float:
        """Get the angle (radian) of the player based of the cursor position on the screen."""
        return (
            math.atan2(
                self.group.viewpoint.y - self.virt_y,
                self.group.viewpoint.x - self.virt_x,
            )
            + 2 * math.pi
        ) % (2 * math.pi)

    @property
    def weapon_angle(self) -> float:
        """Get the angle of the weapon based of the cursor position on the screen."""
        return (
            math.atan2(
                self.group.viewpoint.y - self.virt_weapon_y,
                self.group.viewpoint.x - self.virt_weapon_x,
            )
            + 2 * math.pi
        ) % (2 * math.pi)

    @property
    def weapon_x(self) -> int:
        """Get the real x coordinate of the weapon in the game world."""
        offset1 = 13  # @todo: Remove it!
        offset2 = 15  # @todo: Remove it!
        angle = self.angle
        return round(
            self.x - math.cos(angle - math.pi / 2) * offset1 + math.cos(angle) * offset2
        )

    @property
    def weapon_y(self) -> int:
        """Get the real y coordinate of the weapon in the game world."""
        offset1 = 13  # @todo: Remove it!
        offset2 = 15  # @todo: Remove it!
        angle = self.angle
        return round(
            self.y - math.sin(angle - math.pi / 2) * offset1 + math.sin(angle) * offset2
        )

    @property
    def virt_weapon_x(self) -> int:
        """Get the virtual x coordinate of weapon on the screen."""
        offset1 = 13  # @todo: Remove it!
        offset2 = 15  # @todo: Remove it!
        angle = self.angle
        return round(
            self.virt_x
            - math.cos(angle - math.pi / 2) * offset1
            + math.cos(angle) * offset2
        )

    @property
    def virt_weapon_y(self) -> int:
        """Get the virtual y coordinate of weapon on the screen."""
        offset1 = 13  # @todo: Remove it!
        offset2 = 15  # @todo: Remove it!
        angle = self.angle
        return round(
            self.virt_y
            - math.sin(angle - math.pi / 2) * offset1
            + math.sin(angle) * offset2
        )

    def draw_border(
        self, surface: pg.surface.Surface, sprite: pg.sprite.Sprite
    ) -> None:
        pg.draw.rect(surface, GREEN, self.rect, width=1)
        pg.draw.rect(surface, GREEN, self.bounding_rect, width=1)

    def update(self, dt: int, direction: tuple[int, int]) -> None:
        """Update the player object."""
        # Update player values
        self.direction = direction
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
            self.animate()

        self.move()
        self.rotate()

    def animate(self) -> None:
        # If not attacking.
        if self.movement_state in (MovementState.IDLE, MovementState.MOVE):
            if self.direction[0] != 0 or self.direction[1] != 0:
                # Move state
                self._switch_movement(MovementState.MOVE)
            elif self.direction[0] == 0 and self.direction[1] == 0:
                # Idle state
                self._switch_movement(MovementState.IDLE)

    def move(self) -> None:
        """Move the player in the specific direction."""
        self.group.camera.move(self.move_vector)
        self.collide()

    def rotate(self) -> None:
        """
        Rotate the player object on the center. Need to negate the
        result, if the image starts at the wrong direction.
        """
        # Get pre-rotate image from list and replace
        # old rect/bounding_rect with new one.
        self.image, self.rect, self.bounding_rect = self.sprite.get_rotated_image(
            self.angle, self.virt_x, self.virt_y
        )

    def collide(self):
        """Check for collision with other tiles."""
        for tile in self.group.level.tiles_collision_move.sprites():
            if self.collide_x(tile) and self.collide_y(tile):
                print("collide:", tile)

    def collide_x(self, tile: Tile) -> bool:
        """Check collision on x axis."""
        width = self.bounding_rect.width
        return (
            self.x + width // 2 > tile.x and self.x - width // 2 < tile.x + tile.width
        )

    def collide_y(self, tile: Tile) -> bool:
        """Check collision on y axis."""
        height = self.bounding_rect.height
        return (
            self.y + height // 2 > tile.y
            and self.y - height // 2 < tile.y + tile.height
        )
