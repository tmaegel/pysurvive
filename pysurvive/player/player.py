#!/usr/bin/env python
# coding=utf-8
import math

import pygame as pg

from pysurvive.class_toolchain import Animation
from pysurvive.config import SCREEN_RECT
from pysurvive.logger import logger
from pysurvive.player import Bullet, MovementState, PlayerImages, WeaponsState
from pysurvive.utils import load_sound


class Player(Animation):

    speed = 6
    feets = None
    light = None
    bullet = None

    movement_state = MovementState.IDLE
    weapon_state = WeaponsState.HANDGUN

    def __init__(self, _game, _x, _y):
        Animation.__init__(self)
        # Reference to the game object
        self.game = _game
        # Real position of the player in the game world
        self.x = _x
        self.y = _y

        # Preloading sounds
        self.sound_shot = load_sound("shot/pistol.wav")
        self.sound_reload = load_sound("reload/pistol.wav")

        # Contains the original (scaled only) images of the player object.
        self.images = PlayerImages()
        self.image = self.get_image(frame=0)
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        # Virtual position the image at the center of the screen
        # The position of image/rect used for drawing only
        self.rect.center = (SCREEN_RECT.width // 2, SCREEN_RECT.height // 2)

        # self.feets = PlayerFeet(self)
        # Initialize the light (flashlight) with x and y from player
        # The initial coordinates are used for drawing only.
        # self.light = Flashlight(self, self.get_x(), self.get_y())

    def get_image(self, frame: int) -> pg.Surface:
        # @todo: Is there are a more pythonic way?
        # __get__, __call__ or __getattr__ ?
        return self.images[self.movement_state.value][frame].image

    def update(self, dt, direction):
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
            self.frame %= len(self.images[self.movement_state.value])

            # Handle the different images for animation here
            self.animate(direction)

        # @todo: Not time based yet
        # Check for collision before
        # Allow moving only if there is no collision detected
        if not self.collide_by_move(direction, self.speed):
            self.move(direction, self.speed)

        # Rotate the iamge
        if not self.collide_by_rotation(self.get_weapon_angle()):
            self.rotate(self.get_weapon_angle())

        # Update flashlight of player
        # self.light.update(self.get_x(), self.get_y())

    def move(self, direction, speed):
        """Move the player in the specific direction."""
        dx, dy = self._get_move_vector(direction, speed)
        self.game.set_offset(dx, dy)

        # Add the negate value of dx and dy to the player position
        self.x = round(self.x - dx)
        self.y = round(self.y - dy)

    def rotate(self, angle):
        """
        Rotate the player object on the center. Need to negate the
        result, if the image starts at the wrong direction.

        :param angle: Rotation angle
        """
        self.image = self.images[self.movement_state.value][self.frame].rotate(angle)
        # Recreating mask after every rotation
        self.mask = pg.mask.from_surface(self.image)
        # Keep the image on the same position.
        # Save its current center.
        x, y = self.rect.center
        # Replace old rect with new rect.
        self.rect = self.image.get_rect()
        # Put the new rect's center at old center.
        self.rect.center = (x, y)

    def animate(self, direction):
        if self.frame == len(self.images[self.movement_state.value]) - 1:
            # Rest movement after attacking, shooting or reloading.
            # If attacking
            if self.movement_state == MovementState.MELEEATTACK:
                self.movement_state = MovementState.IDLE
            # If shooting
            elif self.movement_state == MovementState.SHOOT:
                self.movement_state = MovementState.IDLE
                # del self.bullet
            # If reloading
            elif self.movement_state == MovementState.RELOAD:
                self.movement_state = MovementState.IDLE

        # If not attacking, shooting and reloading
        if (
            self.movement_state == MovementState.IDLE
            or self.movement_state == MovementState.MOVE
        ):
            if direction[0] != 0 or direction[1] != 0:
                # Move state
                self.movement_state = MovementState.MOVE
            elif direction[0] == 0 and direction[1] == 0:
                # Idle state
                self.movement_state = MovementState.IDLE

    def shot(self) -> None:
        # Set shot movement
        self.shooting = True
        self.frame = 0
        self.movement_state = MovementState.SHOOT
        self.sound_shot.play()

        # Create bullet object
        self.bullet = Bullet(
            self.get_weapon_x(), self.get_weapon_y(), self.get_weapon_angle()
        )
        self.bullet.intersect = self.bullet.get_intersection(
            self.game.block_sprites.sprites()
        )

    def reload(self) -> None:
        # Set reload movement
        self.reloading = True
        self.frame = 0
        self.movement_state = MovementState.RELOAD
        self.sound_reload.play()

    def collide_by_move(self, direction, speed):
        """
        First check a simple collisions detection (collide rect).
        Then check for a specific collision (mask) for a better collisions.
        """

        # Stop the movement for collision checks
        self.game.set_offset(0, 0)

        # Backup the position of player
        player_rect_x = self.get_virt_x()
        player_rect_y = self.get_virt_y()

        # Get the currect movement vector to simulate the movement
        dx, dy = self._get_move_vector(direction, speed)

        # Simulate the movement by move the rect object
        self.rect.centerx = round(self.rect.centerx - dx)
        self.rect.centery = round(self.rect.centery - dy)

        collision = False
        for block in self._collide_by_rect():
            # Make better check here and handle the collision.
            point = pg.sprite.collide_mask(self, block)
            if point is not None:
                collision = True
                break

        # Reset the simulated changes of player
        self.rect.centerx = player_rect_x
        self.rect.centery = player_rect_y

        return collision

    def collide_by_rotation(self, angle):

        # Backup the player image/mask
        player_image = self.image
        player_mask = self.mask

        def reset() -> None:
            self.image = player_image
            self.mask = player_mask
            # Keep the image on the same position.
            # Save its current center.
            x, y = self.rect.center
            # Replace old rect with new rect.
            self.rect = self.image.get_rect()
            # Put the new rect's center at old center.
            self.rect.center = (x, y)

        # Simulate the rotation of the player
        self.rotate(angle)

        collision = False
        for block in self._collide_by_rect():
            # Make better check here and handle the collision.
            point = pg.sprite.collide_mask(self, block)
            if point is not None:
                collision = True
                break

        # Reset the simulated changes of player
        reset()

        return collision

    def _collide_by_rect(self):
        block_hit_list = pg.sprite.spritecollide(
            self, self.game.block_render_sprites, False, collided=pg.sprite.collide_rect
        )

        return block_hit_list

    def _get_move_vector(self, direction: list[int], speed: int) -> tuple[int]:
        """
        If the player moves diagonal add only the half of the speed
        in each direction.
        """
        if direction[0] != 0 and direction[1] != 0:
            # Based on the 45° angle
            return (
                -1 * direction[0] * abs(math.cos(math.pi / 4)) * speed,
                -1 * direction[1] * abs(math.sin(math.pi / 4)) * speed,
            )
        return (-1 * direction[0] * speed, -1 * direction[1] * speed)

    def get_x(self) -> int:
        """
        Get the real x coordinate of the player in the game world.
        """
        return self.x

    def get_y(self) -> int:
        """
        Get the real y coordinate of the player in the game world.
        """
        return self.y

    def get_virt_x(self) -> int:
        """
        Get the virtual x coordinate of the player on the screen.
        """
        return self.rect.centerx

    def get_virt_y(self) -> int:
        """
        Get the virtual y coordinate of the player on the screen.
        """
        return self.rect.centery

    def get_aim_x(self) -> int:
        """
        Get the x coordinate of the mouse cursor.
        """
        return pg.mouse.get_pos()[0]

    def get_aim_y(self) -> int:
        """
        Get the y coordinate of the mouse cursor.
        """
        return pg.mouse.get_pos()[1]

    def get_angle(self) -> float:
        """
        Get the angle of the player position on the screen
        and the mouse cursor.
        """
        return (
            math.atan2(
                self.get_aim_y() - self.get_virt_y(),
                self.get_aim_x() - self.get_virt_x(),
            )
            + 2 * math.pi
        ) % (2 * math.pi)

    def get_weapon_angle(self) -> float:
        """
        Get the angle of the weapon position on the screen
        and the mouse cursor.
        """
        return (
            math.atan2(
                self.get_aim_y() - self.get_virt_weapon_y(),
                self.get_aim_x() - self.get_virt_weapon_x(),
            )
            + 2 * math.pi
        ) % (2 * math.pi)

    def get_weapon_x(self, offset1: int = 13, offset2: int = 15) -> int:
        """
        Get the real x coordinate of the weapon in the game world.
        """
        angle = self.get_angle()
        return round(
            self.get_x()
            - math.cos(angle - math.pi / 2) * offset1
            + math.cos(angle) * offset2
        )

    def get_weapon_y(self, offset1: int = 13, offset2: int = 15) -> int:
        """
        Get the real y coordinate of the weapon in the game world.
        """
        angle = self.get_angle()
        return round(
            self.get_y()
            - math.sin(angle - math.pi / 2) * offset1
            + math.sin(angle) * offset2
        )

    def get_virt_weapon_x(self, offset1: int = 13, offset2: int = 15) -> int:
        """
        Get the virtual x coordinate of weapon on the screen.
        """
        angle = self.get_angle()
        return round(
            self.get_virt_x()
            - math.cos(angle - math.pi / 2) * offset1
            + math.cos(angle) * offset2
        )

    def get_virt_weapon_y(self, offset1: int = 13, offset2: int = 15) -> int:
        """
        Get the virtual y coordinate of weapon on the screen.
        """
        angle = self.get_angle()
        return round(
            self.get_virt_y()
            - math.sin(angle - math.pi / 2) * offset1
            + math.sin(angle) * offset2
        )
