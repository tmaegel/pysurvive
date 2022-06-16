import os
import math
import pygame as pg

from config import (
    SCREEN_RECT,
    IMAGE_DIR,
    GRAY_LIGHT,
)
from utils import load_image, load_sound
from class_toolchain import Ray, Animation
from flashlight import Flashlight


class Player(Animation):

    scale = 4
    speed = 6

    # Define the single movement states.
    # Each movement state is represented by a dictionary.
    movement_index = 0
    movements = [
        {
            'name': 'idle',
        },
        {
            'name': 'move',
        },
        {
            'name': 'meleeattack',
        },
        {
            'name': 'shoot',
        },
        {
            'name': 'reload',
        },
    ]
    weapon_index = 1
    weapons = [
        'knife',
        'handgun',
        'rifle',
        'shotgun',
    ]

    feets = None
    light = None
    bullet = None

    def __init__(self, _game, _x, _y):
        Animation.__init__(self)
        # Reference to the game object
        self.game = _game
        # Real position of the player in the game world
        self.x = _x
        self.y = _y

        # Preloading images
        for movement in self.movements:
            _images = []
            directory = IMAGE_DIR + 'player/' + \
                self.weapons[self.weapon_index] + \
                '/' + movement['name'] + '/'
            if os.path.isdir(directory):
                path, _, files = next(os.walk(directory))
                for img in sorted(files):
                    if 'spritesheet' not in img:
                        image, _ = load_image(
                            path + img, alpha=True, path=False)
                        _images.append(pg.transform.scale(
                            image, (image.get_rect().width // self.scale,
                                    image.get_rect().height // self.scale)))
                self.images.append(_images)
            else:
                print('warn: Directory ' + directory + ' doesnt exists.')

        # Preloading sounds
        self.sound_shot = load_sound('shot/pistol.wav')
        self.sound_reload = load_sound('reload/pistol.wav')

        self.image = self.images[self.movement_index][0]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        # Virtual position the image at the center of the screen
        # The position of image/rect used for drawing only
        self.rect.center = (SCREEN_RECT.width//2, SCREEN_RECT.height//2)

        self.feets = PlayerFeet(self)
        # Initialize the light (flashlight) with x and y from player
        # The initial coordinates are used for drawing only.
        # self.light = Flashlight(self, self.get_x(), self.get_y())

    def update(self, dt, direction):
        """
        Update the player object.
        """

        # Accumulate time since last update.
        self._next_update += dt
        # If more time has passed as a period, then we need to update.
        if self._next_update >= self._period:
            # Skipping frames if too much time has passed.
            # Since _next_update is bigger than period this is at least 1.
            self.frame += int(self._next_update/self._period)
            # Time that already has passed since last update.
            self._next_update %= self._period
            # Limit the frame to the length of the image list.
            self.frame %= len(self.images[self.movement_index])

            # Handle the different sprites for animation here
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
        """
        Move the player in the specific direction.
        """

        dx, dy = self._get_move_vector(direction, speed)
        self.game.set_offset(dx, dy)

        # Add the negate value of dx and dy to the player position
        self.x = round(self.x - dx)
        self.y = round(self.y - dy)

    def rotate(self, angle):
        """
        Rotate the player object on the center.
        Need to negate the result, if the image starts
        at the wrong direction.

        :param angle: Rotation angle
        """
        self.image = pg.transform.rotate(
            self.images[self.movement_index][self.frame],
            (-1 * angle * (180 / math.pi)))
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
        if self.frame == len(self.images[self.movement_index]) - 1:
            # Rest movement after attacking, shooting or reloading.
            # If attacking
            if self.movement_index == 2:
                self.movement_index = 0
            # If shooting
            elif self.movement_index == 3:
                self.movement_index = 0
                # del self.bullet
            # If reloading
            elif self.movement_index == 4:
                self.movement_index = 0

        # If not attacking, shooting and reloading
        if self.movement_index == 0 or self.movement_index == 1:
            if direction[0] != 0 or direction[1] != 0:
                # Move state
                self.movement_index = 1
            elif direction[0] == 0 and direction[1] == 0:
                # Idle state
                self.movement_index = 0

    def shot(self):
        # Set shot movement
        self.shooting = True
        self.frame = 0
        self.movement_index = 3
        self.sound_shot.play()

        # Create bullet object
        self.bullet = Bullet(self.get_weapon_x(),
                             self.get_weapon_y(), self.get_weapon_angle())
        self.bullet.intersect = self.bullet.get_intersection(
            self.game.block_sprites.sprites())

    def reload(self):
        # Set reload movement
        self.reloading = True
        self.frame = 0
        self.movement_index = 4
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

        def reset():
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
            self, self.game.block_render_sprites, False,
            collided=pg.sprite.collide_rect)

        return block_hit_list

    def _get_move_vector(self, direction, speed):
        # If the player moves diagonal add only the
        # half of the speed in each direction.
        if direction[0] != 0 and direction[1] != 0:
            # Based on the 45° angle
            return (-1 * direction[0] * abs(math.cos(math.pi/4)) * speed,
                    -1 * direction[1] * abs(math.sin(math.pi/4)) * speed)
        else:
            return (-1 * direction[0] * speed,
                    -1 * direction[1] * speed)

    def get_x(self):
        """
        Get the real x coordinate of the player in the game world.
        """
        return self.x

    def get_y(self):
        """
        Get the real y coordinate of the player in the game world.
        """
        return self.y

    def get_virt_x(self):
        """
        Get the virtual x coordinate of the player on the screen.
        """
        return self.rect.centerx

    def get_virt_y(self):
        """
        Get the virtual y coordinate of the player on the screen.
        """
        return self.rect.centery

    def get_aim_x(self):
        """
        Get the x coordinate of the mouse cursor.
        """
        return pg.mouse.get_pos()[0]

    def get_aim_y(self):
        """
        Get the y coordinate of the mouse cursor.
        """
        return pg.mouse.get_pos()[1]

    def get_angle(self):
        """
        Get the angle of the player position on the screen
        and the mouse cursor.
        """
        return (math.atan2(
            self.get_aim_y() - self.get_virt_y(),
            self.get_aim_x() - self.get_virt_x())
            + 2 * math.pi) % (2 * math.pi)

    def get_weapon_angle(self):
        """
        Get the angle of the weapon position on the screen
        and the mouse cursor.
        """
        return (math.atan2(
            self.get_aim_y() - self.get_virt_weapon_y(),
            self.get_aim_x() - self.get_virt_weapon_x())
            + 2 * math.pi) % (2 * math.pi)

    def get_weapon_x(self, offset1=13, offset2=15):
        """
        Get the real x coordinate of the weapon in the game world.
        """
        angle = self.get_angle()
        return round(self.get_x()
                     - math.cos(angle - math.pi/2) * offset1
                     + math.cos(angle) * offset2)

    def get_weapon_y(self, offset1=13, offset2=15):
        """
        Get the real y coordinate of the weapon in the game world.
        """
        angle = self.get_angle()
        return round(self.get_y()
                     - math.sin(angle - math.pi/2) * offset1
                     + math.sin(angle) * offset2)

    def get_virt_weapon_x(self, offset1=13, offset2=15):
        """
        Get the virtual x coordinate of weapon on the screen.
        """
        angle = self.get_angle()
        return round(self.get_virt_x()
                     - math.cos(angle - math.pi/2) * offset1
                     + math.cos(angle) * offset2)

    def get_virt_weapon_y(self, offset1=13, offset2=15):
        """
        Get the virtual y coordinate of weapon on the screen.
        """
        angle = self.get_angle()
        return round(self.get_virt_y()
                     - math.sin(angle - math.pi/2) * offset1
                     + math.sin(angle) * offset2)


class PlayerFeet(Animation):

    """
    A player subclass to hold the feet images / states of the player.
    """

    scale = 5

    # @workaroung: offset (20) for rifle, shutgun and knife
    feet_offset_px = 5

    feet_index = 0
    feets = [
        'idle',
        'walk',
        'walk_left',
        'walk_right',
        'run',
    ]

    def __init__(self, _player):
        Animation.__init__(self)
        self.player = _player

        for feet in self.feets:
            _images = []
            directory = IMAGE_DIR + 'player/feet/' + feet + '/'
            if os.path.isdir(directory):
                path, _, files = next(os.walk(directory))
                for img in sorted(files):
                    if 'spritesheet' not in img:
                        image, _ = load_image(
                            path + img, alpha=True, path=False)
                        _images.append(pg.transform.scale(
                            image, (image.get_rect().width // self.scale,
                                    image.get_rect().height // self.scale)))
                self.images.append(_images)
            else:
                print('warn: Directory ' + directory + ' doesnt exists.')

        self.image = self.images[self.feet_index][self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = (
            round(self.player.get_virt_x()
                  - math.cos(self.player.get_weapon_angle()) *
                  self.feet_offset_px
                  - math.cos(self.player.get_weapon_angle() - math.pi/2)
                  * self.feet_offset_px//2),
            round(self.player.get_virt_y()
                  - math.sin(self.player.get_weapon_angle()) *
                  self.feet_offset_px
                  - math.sin(self.player.get_weapon_angle() - math.pi/2)
                  * self.feet_offset_px//2)
        )

    def update(self, dt, direction):
        """
        Update the player feets object.
        """

        # Accumulate time since last update.
        self._next_update += dt
        # If more time has passed as a period, then we need to update.
        if self._next_update >= self._period:
            # Skipping frames if too much time has passed.
            # Since _next_update is bigger than period this is at least 1.
            self.frame += int(self._next_update/self._period)
            # Time that already has passed since last update.
            self._next_update %= self._period
            # Limit the frame to the length of the image list.
            self.frame %= len(self.images[self.feet_index])

        # @todo: Not time based yet
        self.move(direction)
        self.rotate()

    def move(self, direction):
        """
        Move the player feets in the specific direction.
        """

        self.rect.center = (
            self.player.get_virt_x(),
            self.player.get_virt_y())
        self.rect.center = (
            round(self.player.get_virt_x()
                  - math.cos(self.player.get_weapon_angle()) *
                  self.feet_offset_px
                  - math.cos(self.player.get_weapon_angle() - math.pi/2)
                  * self.feet_offset_px//2),
            round(self.player.get_virt_y()
                  - math.sin(self.player.get_weapon_angle()) *
                  self.feet_offset_px
                  - math.sin(self.player.get_weapon_angle() - math.pi/2)
                  * self.feet_offset_px//2)
        )

        self.rect.move_ip(*[d * self.player.speed for d in direction])

        if direction[0] != 0 or direction[1] != 0:
            # Move state
            self.feet_index = 1
        elif direction[0] == 0 and direction[1] == 0:
            # Idle state
            self.frame = 0
            self.feet_index = 0

    def rotate(self):
        """
        Rotate the player feets object on the center.
        Need to negate the result, if the image starts
        at the wrong direction.
        """

        # Need to negate the result, if the image starts
        # at the wrong direction.
        self.image = pg.transform.rotate(
            self.images[self.feet_index][self.frame],
            (-1 * self.player.get_weapon_angle() * (180 / math.pi)))
        # Keep the image on the same position.
        # Save its current center.
        x, y = self.rect.center
        # Replace old rect with new rect.
        self.rect = self.image.get_rect()
        # Put the new rect's center at old center.
        self.rect.center = (x, y)


class Bullet(Ray):

    # Draw the impact position if true.
    # Otherwise draw the trail of the bullet.
    impact = False

    trail_offset = 25

    def __init__(self, _x, _y, _angle):
        Ray.__init__(self, _x, _y, _angle)

    def draw(self, screen, offset):
        """
        Draw the bullet.
        """

        if self.intersect:
            if self.impact:
                # Draw the impact
                pg.draw.circle(screen, (255, 0, 0),
                               (self.intersect['x'] - offset[0],
                                self.intersect['y'] - offset[1]), 2)
            else:
                # Draw the trail of the bullet
                pg.draw.line(screen, GRAY_LIGHT,
                             (self.x0 - offset[0] + math.cos(self.angle)
                              * self.trail_offset,
                              self.y0 - offset[1] + math.sin(self.angle)
                              * self.trail_offset),
                             (self.intersect['x'] - offset[0],
                              self.intersect['y'] - offset[1]))
                self.impact = True
