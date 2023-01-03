#!/usr/bin/env python
# coding=utf-8
import math

import pygame as pg

from pysurvive.class_toolchain import Animation
from pysurvive.config import DEBUG_SPRITE, FLASHLIGHT_ENABLE, RED, SOUND_DIR
from pysurvive.flashlight import Flashlight
from pysurvive.game.core import Camera, Screen
from pysurvive.player.misc import (
    MovementState,
    PlayerSpritesheet,
    RotatableImage,
    WeaponsState,
)
from pysurvive.player.viewpoint import Viewpoint
from pysurvive.utils import load_sound


class PlayerGroup(pg.sprite.RenderPlain):

    """Sprite group that contains all drawable player sprites."""

    def __init__(self) -> None:
        super().__init__()
        self.viewpoint = Viewpoint()
        self.player = Player(self)  # Absolute position in game world.
        self.add(
            (
                self.viewpoint,
                self.player,
            )
        )

    def draw(self, surface: pg.Surface) -> list[pg.Rect]:
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


class Player(Animation):

    """Player object/sprite."""

    def __init__(self, _group) -> None:
        super().__init__()
        self.group = _group  # Reference to the group with other player object.
        self.screen = Screen()
        self.camera = Camera()
        self.light = None  # Reference to the players flashlight.
        self.x = self.camera.centerx  # Absolute x coordinate of player in the world.
        self.y = self.camera.centery  # Absolute x coordinate of player in the world.
        self.speed = 6
        self.direction = (0, 0)
        self.player_type = "default"
        self.movement_state = MovementState.IDLE
        self.old_movement_state = self.movement_state
        self.weapon_state = WeaponsState.HANDGUN

        # Contains the original (scaled only) images of the player object.
        # @todo: Loading other weapon-movement images too.
        self.images = PlayerSpritesheet(
            custom_path=f"{self.player_type}/{self.weapon_state.name.lower()}"
        )
        self.image = self.active_image
        self.mask = pg.mask.from_surface(self.image)  # For collision detection.
        # Acts as the virtual position (center of the screen) of the player.
        self.rect = self.image.get_rect()
        # Virtual position the image at the center of the screen
        # The position of image/rect used for drawing only
        self.rect.center = (self.screen.centerx, self.screen.centery)

        # Preloading sounds
        self.sound_shot = load_sound(f"{SOUND_DIR}/shot/pistol.wav")
        self.sound_reload = load_sound(f"{SOUND_DIR}/reload/pistol.wav")

        if FLASHLIGHT_ENABLE:
            # Initialize the light (flashlight) with x and y from player
            # The initial coordinates are used for drawing only.
            self.light = Flashlight(self, self.x, self.y)

    @property
    def active_image_object(self) -> RotatableImage:
        """Returns the active image object (RotatableImage)."""
        return self.images[self.movement_state.value][self.frame]

    @property
    def active_image(self) -> pg.Surface:
        """Returns the active raw image of the active RotatableImage."""
        return self.active_image_object.image

    @property
    def virt_pos(self) -> tuple[int, int]:
        """Get the virtual rect position of the player on the screen."""
        return self.rect.center

    @property
    def virt_x(self) -> int:
        """Get the virtual x coordinate of the player on the screen."""
        return self.rect.centerx

    @property
    def virt_y(self) -> int:
        """Get the virtual y coordinate of the player on the screen."""
        return self.rect.centery

    @property
    def angle(self) -> float:
        """Get the angle of the player position on the screen."""
        return (
            math.atan2(
                self.group.viewpoint.y - self.virt_y,
                self.group.viewpoint.x - self.virt_x,
            )
            + 2 * math.pi
        ) % (2 * math.pi)

    @property
    def weapon_angle(self) -> float:
        """Get the angle of the weapon position on the screen."""
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

    @property
    def move_vector(self) -> tuple[float, float]:
        """
        If the player moves diagonal add only the half of the speed
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

    def draw_border(self, surface: pg.Surface, sprite: pg.sprite.Sprite):
        pg.draw.rect(surface, RED, sprite.rect, width=1)

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
            self.frame %= len(self.images[self.movement_state.value])

            # Handle the different images for animation here
            self.animate()

        # @todo: Not time based yet
        # Check for collision before
        # Allow moving only if there is no collision detected
        if not self.collide_by_move():
            self.move()
        # Rotate the iamge
        # if not self.collide_by_rotation(self.weapon_angle):
        self.rotate(self.weapon_angle)
        if FLASHLIGHT_ENABLE:
            # Update flashlight of player
            self.light.update(self.x, self.y)

    def move(self) -> None:
        """Move the player in the specific direction."""
        dx, dy = self.move_vector
        self.camera.position = (dx, dy)
        # Add the negate value of dx and dy to the player position
        self.x = round(self.x - dx)
        self.y = round(self.y - dy)

    def rotate(self, angle: float) -> None:
        """
        Rotate the player object on the center. Need to negate the
        result, if the image starts at the wrong direction.

        :param angle: Rotation angle
        """
        self.image = self.active_image_object.rotate(angle)
        # Recreating mask after every rotation
        self.mask = pg.mask.from_surface(self.image)
        # Keep the image on the same position.
        # Save its current center.
        x, y = self.virt_pos
        # Replace old rect with new rect.
        self.rect = self.image.get_rect()
        # Put the new rect's center at old center.
        self.rect.center = (x, y)

    def animate(self) -> None:
        # If not attacking.
        if self.movement_state in (MovementState.IDLE, MovementState.MOVE):
            if self.direction[0] != 0 or self.direction[1] != 0:
                # Move state
                self._switch_movement(MovementState.MOVE)
            elif self.direction[0] == 0 and self.direction[1] == 0:
                # Idle state
                self._switch_movement(MovementState.IDLE)

    def _switch_movement(self, movement_state: MovementState) -> None:
        self.old_movement_state = self.movement_state  # Save old state
        self.movement_state = movement_state
        # Reset frame if movement_state differ.
        if self.old_movement_state != self.movement_state:
            self.frame = 0

    def collide_by_move(self) -> bool:
        """
        First check a simple collisions detection (collide rect).
        Then check for a specific collision (mask) for a better collisions.
        """

        # Stop the movement for collision checks
        self.camera.position = (0, 0)

        # Backup the position of player
        player_rect_x = self.virt_x
        player_rect_y = self.virt_y

        # Get the currect movement vector to simulate the movement
        dx, dy = self.move_vector

        # Simulate the movement by move the rect object
        self.rect.centerx = round(self.virt_x - dx)
        self.rect.centery = round(self.virt_y - dy)

        collision = False
        # for block in self._collide_by_rect():
        #     # Make better check here and handle the collision.
        #     point = pg.sprite.collide_mask(self, block)
        #     if point is not None:
        #         collision = True
        #         break

        # Reset the simulated changes of player
        self.rect.centerx = player_rect_x
        self.rect.centery = player_rect_y

        return collision

    def collide_by_rotation(self, angle: float) -> bool:
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

    def _collide_by_rect(self) -> list[pg.sprite.Sprite]:
        block_hit_list = pg.sprite.spritecollide(
            self,
            self.group.game.block_render_sprites,
            False,
            collided=pg.sprite.collide_rect,
        )

        return block_hit_list
