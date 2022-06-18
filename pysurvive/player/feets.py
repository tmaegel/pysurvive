#!/usr/bin/env python
# coding=utf-8
import math

import pygame as pg

from pysurvive.class_toolchain import Animation
from pysurvive.player.misc import FeetMovementState, PlayerImages, RotatableImage


class PlayerFeet(Animation):

    """
    A player subclass to hold the feet images / states of the player.
    """

    # @workaroung: offset (20) for rifle, shutgun and knife
    feet_offset_px = 5

    def __init__(self, _group):
        super().__init__()
        self.group = _group  # Reference to the group with other player object.
        self.direction = (0, 0)
        self.movement_state = FeetMovementState.IDLE

        # Contains the original (scaled only) images of the player feets object.
        self.images = PlayerImages(
            custom_path="feet", movement_states=FeetMovementState
        )
        self.image = self.active_image
        self.rect = self.image.get_rect()
        self.rect.center = (
            round(
                self.group.player.virt_x
                - math.cos(self.group.player.weapon_angle) * self.feet_offset_px
                - math.cos(self.group.player.weapon_angle - math.pi / 2)
                * self.feet_offset_px
                // 2
            ),
            round(
                self.group.player.virt_y
                - math.sin(self.group.player.weapon_angle) * self.feet_offset_px
                - math.sin(self.group.player.weapon_angle - math.pi / 2)
                * self.feet_offset_px
                // 2
            ),
        )

    @property
    def active_image_object(self) -> RotatableImage:
        """Returns the active image object (RotatableImage)."""
        return self.images[self.movement_state.value][self.frame]

    @property
    def active_image(self) -> pg.Surface:
        """Returns the active raw image of the active RotatableImage."""
        return self.active_image_object.image

    def update(self, dt: int, direction: tuple[int, int]) -> None:
        """Update the player feets object."""
        # Update player feets values
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
            self.frame %= len(self.images[self.movement_state.value])

        # @todo: Not time based yet
        self.move()
        self.rotate()

    def move(self) -> None:
        """Move the player feets in the specific direction."""
        self.rect.center = (self.group.player.virt_x, self.group.player.virt_y)
        self.rect.center = (
            round(
                self.group.player.virt_x
                - math.cos(self.group.player.weapon_angle) * self.feet_offset_px
                - math.cos(self.group.player.weapon_angle - math.pi / 2)
                * self.feet_offset_px
                // 2
            ),
            round(
                self.group.player.virt_y
                - math.sin(self.group.player.weapon_angle) * self.feet_offset_px
                - math.sin(self.group.player.weapon_angle - math.pi / 2)
                * self.feet_offset_px
                // 2
            ),
        )
        self.rect.move_ip(*[d * self.group.player.speed for d in self.direction])

        if self.direction[0] != 0 or self.direction[1] != 0:
            # Move state
            self.movement_state = FeetMovementState.WALK
        elif self.direction[0] == 0 and self.direction[1] == 0:
            # Idle state
            self.frame = 0
            self.movement_state = FeetMovementState.IDLE

    def rotate(self) -> None:
        """
        Rotate the player feets object on the center.
        Need to negate the result, if the image starts
        at the wrong direction.
        """
        self.image = self.active_image_object.rotate(self.group.player.angle)
        # Keep the image on the same position.
        # Save its current center.
        x, y = self.rect.center
        # Replace old rect with new rect.
        self.rect = self.image.get_rect()
        # Put the new rect's center at old center.
        self.rect.center = (x, y)
