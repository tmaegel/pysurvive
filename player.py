import os
import math
import pygame as pg

from config import (
    SCREEN_RECT,
    IMAGE_DIR,
    YELLOW,
    GRAY_LIGHT,
)
from utils import load_image, load_sound
from class_toolchain import Ray
from flashlight import Flashlight


class Player(pg.sprite.Sprite):

    speed = 6

    image_index = 0
    # Contains the original images
    movement_images_orig = []
    # Contains the scaled images
    movement_images = []

    movement_index = 0
    movement_states = [
        'idle',
        'move',
        'meleeattack',
        'shoot',
        'reload',
    ]
    weapon_index = 1
    weapon_status = [
        'knife',
        'handgun',
        'rifle',
        'shotgun',
    ]

    light = None
    bullet = None

    shooting = False
    reloading = False

    # This limit the speed of the activity.
    # The next image of that animation is switch
    # if e.g. reload_index == reload_speed and is reset.
    reload_index = 0
    reload_speed = 1

    def __init__(self, _game):
        # call Sprite initializer
        pg.sprite.Sprite.__init__(self)

        # Preloading images
        for movement in self.movement_states:
            images_orig = []
            images = []
            directory = IMAGE_DIR + 'player/' + \
                self.weapon_status[self.weapon_index] + '/' + movement + '/'
            if os.path.isdir(directory):
                path, _, files = next(os.walk(directory))
                for img in sorted(files):
                    image, _ = load_image(path + img, alpha=True, path=False)
                    images_orig.append(image)
                    images.append(pg.transform.scale(
                        image, (image.get_rect().width//3,
                                image.get_rect().height//3)))
                self.movement_images_orig.append(images_orig)
                self.movement_images.append(images)
            else:
                print('warn: Directory ' + directory + ' doesnt exists.')

        # Preloading sounds
        self.sound_shot = load_sound('shot/pistol.wav')
        self.sound_reload = load_sound('reload/pistol.wav')

        self.image = self.movement_images[self.movement_index][
            self.image_index]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        # Virtual position the image at the center of the screen
        # The position of image/rect used for drawing only
        self.rect.center = (SCREEN_RECT.width//2, SCREEN_RECT.height//2)

        # Real position of the player in the game world
        self.x = self.rect.centerx
        self.y = self.rect.centery

        # Reference to the game object
        self.game = _game

        self.feets = PlayerFeet(self)
        # Initialize the light (flashlight) with x and y from player
        # The initial coordinates are used for drawing only.
        self.light = Flashlight(self, self.get_real_x(), self.get_real_y())

    def update(self, _direction):
        """
        Update the player object.
        This is the crank to all other function calls.
        """

        # Check for collision before
        # Allow moving only if there is no collision detected
        if not self.collide_by_move(_direction, self.speed):
            self.move(_direction, self.speed)

        # Rotate the iamge
        if not self.collide_by_rotation(self.get_angle()):
            self.rotate(self.get_angle())

        # Handle the different sprites for animation here
        self.animate(_direction)

        # Update flashlight of player
        self.light.update(self.get_real_x(), self.get_real_y())

    def shot(self):
        # Set shot movement
        self.shooting = True
        self.image_index = 0
        self.movement_index = 3
        self.sound_shot.play()
        # Create bullet object
        self.bullet = Bullet(
            self.get_real_x(), self.get_real_y(), self.get_angle())
        self.bullet.intersect = self.bullet.get_intersection(
            self.game.wall_sprites.sprites())

    def reload(self):
        # Set reload movement
        self.reloading = True
        self.image_index = 0
        self.movement_index = 4
        self.sound_reload.play()

    def move(self, _direction, _speed):
        """
        Move the player in the specific direction.
        """

        _dx, _dy = self._get_move_vector(_direction, _speed)
        self.game.set_offset(_dx, _dy)

        # Add the negate value of dx and dy to the player position
        self.x = round(self.x - self.game.dx)
        self.y = round(self.y - self.game.dy)

        if self.feets:
            self.feets.move(_direction)

    def _get_move_vector(self, _direction, _speed):
        # If the player moves diagonal add only the
        # half of the speed in each direction.
        if _direction[0] != 0 and _direction[1] != 0:
            # Based on the 45° angle
            return (-1 * _direction[0] * abs(math.cos(math.pi/4)) * _speed,
                    -1 * _direction[1] * abs(math.sin(math.pi/4)) * _speed)
        else:
            return (-1 * _direction[0] * _speed,
                    -1 * _direction[1] * _speed)

    def rotate(self, _angle):
        """
        Rotate the player object on the center.
        Need to negate the result, if the image starts
        at the wrong direction.

        :param angle: Rotation angle
        """
        self.image = pg.transform.rotate(
            self.movement_images[self.movement_index][self.image_index],
            (-1 * _angle * (180 / math.pi)))
        # Recreating mask after every rotation
        self.mask = pg.mask.from_surface(self.image)
        # Keep the image on the same position.
        # Save its current center.
        x, y = self.rect.center
        # Replace old rect with new rect.
        self.rect = self.image.get_rect()
        # Put the new rect's center at old center.
        self.rect.center = (x, y)

    def animate(self, _direction):
        # Increase the image_index if there is a movement only
        if not self.shooting and not self.reloading:
            if _direction[0] != 0 or _direction[1] != 0:
                # Move state
                self.movement_index = 1
            elif _direction[0] == 0 and _direction[1] == 0:
                # Idle state
                self.movement_index = 0

        # Increase the image index. The reset of the image index
        # depends on the movement index.
        if ((self.image_index + 1)
                < len(self.movement_images[self.movement_index])):
            # If idle
            if self.movement_index == 0:
                self.image_index += 1
            # If moving
            elif self.movement_index == 1:
                self.image_index += 1
            # If attacking
            elif self.movement_index == 2:
                self.image_index += 1
            # If shooting
            elif self.movement_index == 3:
                self.image_index += 1
            # If reloading
            elif self.movement_index == 4:
                self.image_index += 1
            else:
                self.image_index += 1
        else:
            # If idle
            if self.movement_index == 0:
                self.image_index = 0
            # If moving
            elif self.movement_index == 1:
                self.image_index = 0
            # If attacking
            elif self.movement_index == 2:
                self.image_index = 0
            # If shooting
            elif self.movement_index == 3:
                # rest movement after shooting
                self.image_index = 0
                self.movement_index = 0
                self.shooting = False
                # If shot is finished, delete bullet object
                del self.bullet
            # If reloading
            elif self.movement_index == 4:
                # reset movement after reloading
                self.image_index = 0
                self.movement_index = 0
                self.reloading = False
            else:
                self.image_index = 0

        # self.feets.move(direction)

    def collide_by_move(self, _direction, _speed):
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
        _dx, _dy = self._get_move_vector(_direction, _speed)

        # Simulate the movement by move the rect object
        self.rect.centerx = round(self.rect.centerx - _dx)
        self.rect.centery = round(self.rect.centery - _dy)

        collision = False
        for wall in self._collide_by_rect():
            # Make better check here and handle the collision.
            point = pg.sprite.collide_mask(self, wall)
            if point is not None:
                collision = True
                break

        # Reset the simulated changes of player
        self.rect.centerx = player_rect_x
        self.rect.centery = player_rect_y

        return collision

    def collide_by_rotation(self, _angle):

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
        self.rotate(_angle)

        collision = False
        for wall in self._collide_by_rect():
            # Make better check here and handle the collision.
            point = pg.sprite.collide_mask(self, wall)
            if point is not None:
                collision = True
                break

        # Reset the simulated changes of player
        reset()

        return collision

    def _collide_by_rect(self):
        wall_hit_list = pg.sprite.spritecollide(
            self, self.game.wall_render_sprites, False,
            collided=pg.sprite.collide_rect)

        return wall_hit_list

    def get_angle(self):
        """
        Calculate the angle of the view based in the mouse position
        """
        angle = (math.atan2(
            self.get_aim_y() - self.get_virt_y(),
            self.get_aim_x() - self.get_virt_x())
            + 2 * math.pi) % (2 * math.pi)

        return angle

    def get_real_x(self):
        return self.x

    def get_real_y(self):
        return self.y

    def get_virt_x(self):
        return self.rect.centerx

    def get_virt_y(self):
        return self.rect.centery

    def get_aim_x(self):
        return pg.mouse.get_pos()[0]

    def get_aim_y(self):
        return pg.mouse.get_pos()[1]


class PlayerFeet(pg.sprite.Sprite):

    """
    A player subclass to hold the feet images / states of the player.
    """

    # @workaroung: offset (20) for rifle, shutgun and knife
    feet_offset_px = 10

    image_index = 0
    feet_index = 0
    feet_states = [
        'idle',
        'walk',
        'walk_left',
        'walk_right',
        'run',
    ]

    def __init__(self, _player):
        # call Sprite initializer
        pg.sprite.Sprite.__init__(self)
        self.player = _player

        # Contains the original images
        self.feet_images_orig = []
        # Contains the scaled images
        self.feet_images = []

        for feet in self.feet_states:
            images_orig = []
            images = []
            directory = IMAGE_DIR + 'player/feet/' + feet + '/'
            if os.path.isdir(directory):
                path, _, files = next(os.walk(directory))
                for img in sorted(files):
                    image, _ = load_image(
                        path + img, alpha=True, path=False)
                    images_orig.append(image)
                    images.append(pg.transform.scale(
                        image, (image.get_rect().width//3,
                                image.get_rect().height//3)))
                self.feet_images_orig.append(images_orig)
                self.feet_images.append(images)
            else:
                print('warn: Directory ' + directory + ' doesnt exists.')

        self.image = self.feet_images[self.feet_index][self.image_index]
        self.rect = self.image.get_rect()
        self.rect.center = (
            round(self.player.get_virt_x()
                  - math.cos(self.player.get_angle()) * self.feet_offset_px
                  - math.cos(self.player.get_angle() - math.pi/2)
                  * self.feet_offset_px//2),
            round(self.player.get_virt_y()
                  - math.sin(self.player.get_angle()) * self.feet_offset_px
                  - math.sin(self.player.get_angle() - math.pi/2)
                  * self.feet_offset_px//2)
        )

    def move(self, direction):
        self.rect.center = (
            self.player.get_virt_x(),
            self.player.get_virt_y())
        self.rect.center = (
            round(self.player.get_virt_x()
                  - math.cos(self.player.get_angle()) * self.feet_offset_px
                  - math.cos(self.player.get_angle() - math.pi/2)
                  * self.feet_offset_px//2),
            round(self.player.get_virt_y()
                  - math.sin(self.player.get_angle()) * self.feet_offset_px
                  - math.sin(self.player.get_angle() - math.pi/2)
                  * self.feet_offset_px//2)
        )
        # Need to negate the result, if the image starts
        # at the wrong direction.
        self.image = pg.transform.rotate(
            self.feet_images[self.feet_index][self.image_index],
            (-1 * self.player.get_angle() * (180 / math.pi)))
        # Keep the image on the same position.
        # Save its current center.
        x, y = self.rect.center
        # Replace old rect with new rect.
        self.rect = self.image.get_rect()
        # Put the new rect's center at old center.
        self.rect.center = (x, y)

        self.rect.move_ip(*[d * self.player.speed for d in direction])

        # Increase the image_index if there is a movement only
        if direction[0] != 0 or direction[1] != 0:
            # Move state
            # if direction[0] < 0 and direction[1] == 0:
            #     # walk left state
            #     self.feet_index = 2
            # elif direction[0] > 0 and direction[1] == 0:
            #     # walk right state
            #     self.feet_index = 3
            # else:
            self.feet_index = 1

            if ((self.image_index + 1)
                    < len(self.feet_images[self.feet_index])):
                self.image_index += 1
            else:
                self.image_index = 0
        elif direction[0] == 0 and direction[1] == 0:
            # Idle state
            self.feet_index = 0
            self.image_index = 0


class Bullet(Ray):

    speed = 5
    size = 50

    # Draw the impact position if true.
    # Otherwise draw the trail of the bullet.
    impact = False

    def __init__(self, _x, _y, _angle):
        Ray.__init__(self, _x, _y, _angle)
        # x, y start coordinates of the bullet (for movement).
        self.x1 = _x
        self.y1 = _y
        # x, y end coordinates of the bullet (for movement).
        self.x2 = self.x1 + math.cos(self.angle) * self.size
        self.y2 = self.y1 + math.sin(self.angle) * self.size

    # def update(self):
    #     self.x1 = self.x1 + math.cos(self.angle) * self.size * self.speed
    #     self.y1 = self.y1 + math.sin(self.angle) * self.size * self.speed
    #     self.x2 = self.x2 + math.cos(self.angle) * self.size * self.speed
    #     self.y2 = self.y2 + math.sin(self.angle) * self.size * self.speed

    def draw(self, screen, _offset):
        """
        Draw the bullet.
        """

        if self.intersect:
            if self.impact:
                # Draw the impact
                pg.draw.circle(screen, YELLOW,
                               (self.intersect['x'] + _offset[0],
                                self.intersect['y'] + _offset[1]), 2)
            else:
                # Draw the trail of the bullet
                pg.draw.line(screen, GRAY_LIGHT,
                             (self.x0 + _offset[0], self.y0 + _offset[1]),
                             (self.intersect['x'] + _offset[0],
                              self.intersect['y'] + _offset[1]))
                self.impact = True
