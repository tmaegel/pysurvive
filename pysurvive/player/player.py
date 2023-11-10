#!/usr/bin/env python
# coding=utf-8
import math
import multiprocessing
from typing import Optional

import pygame as pg

from pysurvive.config import DEBUG_SPRITE, RED
from pysurvive.game.core import Camera
from pysurvive.map.level import Level
from pysurvive.player.feets import PlayerFeets
from pysurvive.player.misc import (
    AnimatedSprite,
    Spritesheet,
    UpperBodyState,
    WeaponsState,
)
from pysurvive.player.viewpoint import Viewpoint


class PlayerGroup(pg.sprite.Group):

    """Sprite group that contains all drawable player sprites."""

    def __init__(self, camera: Camera, viewpoint: Viewpoint) -> None:
        super().__init__()
        self.feets = PlayerFeets()
        self.player = Player(camera, viewpoint, self.feets, x=500, y=600)
        self.add((self.player, self.feets))

    def update(self, dt: float, level: Level) -> None:
        self.player.update(dt, level)
        self.feets.update(dt, target=self.player)

    def draw(self, surface: pg.surface.Surface, camera: Camera) -> None:
        """Custom variant of the builtin method draw()."""
        for sprite in self.sprites():
            offset = sprite.rect.topleft - camera.offset
            surface.blit(sprite.image, offset)
            if DEBUG_SPRITE and hasattr(sprite, "bounding_rect"):
                rect = sprite.bounding_rect.copy()
                rect.x = offset.x + sprite.bounding_rect_offset_x
                rect.y = offset.y + sprite.bounding_rect_offset_y
                pg.draw.rect(surface, RED, rect, width=1)


class Player(AnimatedSprite):

    """Player class."""

    def __init__(
        self,
        camera: Camera,
        viewpoint: Viewpoint,
        feets: PlayerFeets,
        x: int,
        y: int,
    ) -> None:
        super().__init__()
        self.camera = camera
        self.viewpoint = viewpoint
        self.feets = feets

        self.movement_state = UpperBodyState.IDLE
        self.weapon_state = WeaponsState.HANDGUN

        spritesheet_paths = []
        for movement in UpperBodyState:
            for weapon in (self.weapon_state,):
                spritesheet_paths.append(
                    f"player/default/weapons/{weapon.name.lower()}/{movement.name.lower()}"
                )
        with multiprocessing.Pool() as pool:
            self.sprites = pool.map(Spritesheet, spritesheet_paths)
        for spritesheet in self.sprites:
            for image in spritesheet:
                image.deserialize()

        # Ensure to set rect first. Otherwise rect is None in image setter.
        self.rect = self.sprite.image.get_frect(center=(x, y))
        self.image = self.sprite.image
        self.bounding_rect = pg.FRect(self.image.get_bounding_rect())

    @property
    def x(self) -> float:
        return self.rect.centerx

    @property
    def y(self) -> float:
        return self.rect.centery

    @x.setter
    def x(self, _x: float) -> None:
        self.rect.centerx = _x
        self.bounding_rect.x = self.rect.x + self.bounding_rect_offset_x

    @y.setter
    def y(self, _y: float) -> None:
        self.rect.centery = _y
        self.bounding_rect.y = self.rect.y + self.bounding_rect_offset_y

    @property
    def angle(self) -> float:
        """Get the angle (radian) of the player based of the
        cursor position on the screen."""
        return (
            math.atan2(
                self.viewpoint.y - (self.y - self.camera.y),
                self.viewpoint.x - (self.x - self.camera.x),
            )
            + 2 * math.pi
        ) % (2 * math.pi)

    @property
    def image(self) -> Optional[pg.surface.Surface]:
        """Overwrite getter of pg.sprite.Sprite."""
        return self.__image

    @image.setter
    def image(self, _image: Optional[pg.surface.Surface]) -> None:
        """Overwrite setter of pg.sprite.Sprite to always center the rect."""
        _rect = _image.get_frect()
        _rect.center = (self.x, self.y)
        self.__image = _image
        self.rect = _rect
        self.bounding_rect = pg.FRect(_image.get_bounding_rect())

    @property
    def bounding_rect(self) -> Optional[pg.FRect]:
        return self._bounding_rect

    @bounding_rect.setter
    def bounding_rect(self, _bounding_rect: Optional[pg.FRect]) -> None:
        self._bounding_rect = _bounding_rect
        # The initial x, y of the bounding_rect are the offsets for the bounding rect.
        self.bounding_rect_offset_x = _bounding_rect.x
        self.bounding_rect_offset_y = _bounding_rect.y
        self._bounding_rect.x = self.rect.x + _bounding_rect.x
        self._bounding_rect.y = self.rect.y + _bounding_rect.y

    # @todo.....
    @property
    def move_vector(self) -> tuple[float, float]:
        """If the object moves diagonal add only the half of the speed
        in each direction."""
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

    def input(self):
        keystate = pg.key.get_pressed()
        self.direction.x = keystate[pg.K_d] - keystate[pg.K_a]
        self.direction.y = keystate[pg.K_s] - keystate[pg.K_w]
        self.feets.input(self.direction)  # Update player feets direction.

    def update(self, dt: float, level: Level) -> None:
        super().update(dt)

        # Process input.
        self.input()

        # Move player considerung the collision.
        tiles = level.tiles.tiles_movement_collision_on_screen.sprites()
        self.move(dt, tiles)
        # Rotate player considerung the collision.
        self.rotate(self.angle, tiles)

        # Move camera base on the player position.
        self.camera.update(target=self)

    def move(self, dt: float, group: pg.sprite.Group) -> None:
        x_orig = self.x
        for dx in range(1, round(self.speed * dt) + 1):
            x_prev = self.x
            self.x = x_orig + dx * self.direction.x
            if bool(pg.sprite.spritecollide(self, group, False, self.is_collided)):
                self.x = x_prev
                break

        y_orig = self.y
        for dy in range(1, round(self.speed * dt) + 1):
            y_prev = self.y
            self.y = y_orig + dy * self.direction.y
            if bool(pg.sprite.spritecollide(self, group, False, self.is_collided)):
                self.y = y_prev
                break

    def rotate(self, angle: float, group: pg.sprite.Group) -> None:
        """Try to rotate. If collide the image (rect, bounding_rect) will be reset."""
        image_orig = self.image
        # Try to rotate, if collide reset.
        self.image = self.sprite.rotate(angle)
        if bool(pg.sprite.spritecollide(self, group, False, self.is_collided)):
            self.image = image_orig
        else:
            # Rotate player feets omly if there is no collision.
            self.feets.rotate(angle)

    def is_collided(self, player, tile) -> bool:
        """Callback function for check_collision."""
        return player.bounding_rect.colliderect(tile.bounding_rect)

    def animate(self) -> None:
        super().animate()


# class Player(PlayerCore):
#
#     """Player object/sprite."""
#
#     def __init__(self, _group) -> None:
#         super().__init__(_group)
#         self.movement_state = UpperBodyState.IDLE
#         self.weapon_state = WeaponsState.HANDGUN
#
#         spritesheet_paths = []
#         for movement in UpperBodyState:
#             for weapon in (self.weapon_state,):
#                 spritesheet_paths.append(
#                     f"player/default/weapons/{weapon.name.lower()}/{movement.name.lower()}"
#                 )
#         with multiprocessing.Pool() as pool:
#             self.sprites = pool.map(Spritesheet, spritesheet_paths)
#         for spritesheet in self.sprites:
#             for image in spritesheet:
#                 image.deserialize()
#
#         # Initialize sprite image.
#         self.image = self.sprite.image
#         # Rect acts as the virtual position (center of the screen).
#         self.rect = self.sprite.rect
#         # Virtual position the image at the center of the screen.
#         # The position of image/rect used for drawing only.
#         self.rect.center = (
#             self.group.camera.screenx,
#             self.group.camera.screeny,
#         )
#         # Initialize the bounding rect.
#         self.bounding_rect = self.image.get_bounding_rect()
#
#     @property
#     def weapon_angle(self) -> float:
#         """Get the angle of the weapon based of the cursor position
#         on the screen."""
#         return (
#             math.atan2(
#                 self.group.viewpoint.y - self.virt_weapon_y,
#                 self.group.viewpoint.x - self.virt_weapon_x,
#             )
#             + 2 * math.pi
#         ) % (2 * math.pi)
#
#     @property
#     def weapon_x(self) -> int:
#         """Get the real x coordinate of the weapon in the game world."""
#         offset1 = 13  # @todo: Remove it!
#         offset2 = 15  # @todo: Remove it!
#         angle = self.angle
#         return round(
#             self.x - math.cos(angle - math.pi / 2) * offset1 + math.cos(angle) * offset2
#         )
#
#     @property
#     def weapon_y(self) -> int:
#         """Get the real y coordinate of the weapon in the game world."""
#         offset1 = 13  # @todo: Remove it!
#         offset2 = 15  # @todo: Remove it!
#         angle = self.angle
#         return round(
#             self.y - math.sin(angle - math.pi / 2) * offset1 + math.sin(angle) * offset2
#         )
#
#     @property
#     def virt_weapon_x(self) -> int:
#         """Get the virtual x coordinate of weapon on the screen."""
#         offset1 = 13  # @todo: Remove it!
#         offset2 = 15  # @todo: Remove it!
#         angle = self.angle
#         return round(
#             self.virt_x
#             - math.cos(angle - math.pi / 2) * offset1
#             + math.cos(angle) * offset2
#         )
#
#     @property
#     def virt_weapon_y(self) -> int:
#         """Get the virtual y coordinate of weapon on the screen."""
#         offset1 = 13  # @todo: Remove it!
#         offset2 = 15  # @todo: Remove it!
#         angle = self.angle
#         return round(
#             self.virt_y
#             - math.sin(angle - math.pi / 2) * offset1
#             + math.sin(angle) * offset2
#         )
#
#     def rect_range_of_movement(self, speed_per_frame: float) -> pg.FRect:
#         """Returns the rect that covers the movement (speed) of the current frame
#         around the player in each direction."""
#         return pg.FRect(
#             self.x - self.width / 2 - speed_per_frame,
#             self.y - self.height / 2 - speed_per_frame,
#             self.width + speed_per_frame * 2,
#             self.height + speed_per_frame * 2,
#         )
#
#     def update(self, dt: float, direction: tuple[int, int]) -> None:
#         """Update the player upper body."""
#         super().update(dt, direction)
#
#         self.camera.update(target=self.player)
#         speed_per_frame = self.speed * dt
#         self.group.camera.x = self.group.camera.x + self.speed * dt * direction[0]
#         self.group.camera.y = self.group.camera.y + self.speed * dt * direction[1]
#
#         closest_tiles = self.group.level.tiles.tiles_movement_collision.sprites()
#         # closest_tiles = self.group.level.tiles_collision_move.closest_sprites(
#         # rect=self.rect_range_of_movement(speed_per_frame)
#         # )
#         # self.partial_move_x(direction[0], speed_per_frame, closest_tiles)
#         # self.partial_move_y(direction[1], speed_per_frame, closest_tiles)
#
#         self.rotate()
#
#     def rotate(self) -> None:
#         """Rotate the player upper body sprite on the center."""
#         # Rotate the image and get the pre-calculated bounding rect from list
#         # and replace old rect/bounding_rect with new one.
#         self.image, self.rect, self.bounding_rect = self.sprite.rotate(
#             self.angle, self.virt_x, self.virt_y
#         )
