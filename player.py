import os
import math
import pygame as pg

from config import (
    SCREEN_RECT,
    IMAGE_DIR,
)
from utils import load_image
from flashlight import Flashlight


class Player(pg.sprite.Sprite):

    speed = 4
    image_index = 0
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

    def __init__(self, _world):
        # call Sprite initializer
        pg.sprite.Sprite.__init__(self)

        # Contains the original images
        self.movement_images_orig = []
        # Contains the scaled images
        self.movement_images = []

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
                        image, (image.get_rect().width//2,
                                image.get_rect().height//2)))
                self.movement_images_orig.append(images_orig)
                self.movement_images.append(images)
            else:
                print('warn: Directory ' + directory + ' doesnt exists.')

        self.image = self.movement_images[self.movement_index][
            self.image_index]
        self.rect = self.image.get_rect()
        # Virtual position the image at the center of the screen
        # The position of image/rect used for drawing only
        self.rect.center = (SCREEN_RECT.width//2, SCREEN_RECT.height//2)

        # Real position of the player in the world
        self.x = self.rect.centerx
        self.y = self.rect.centery

        # Reference to the world object
        self.world = _world

        # self.feets = PlayerFeet(self)
        # Initialize the light (flashlight) with x and y from player
        # The initial coordinates are used for drawing only.
        self.light = Flashlight(self, self.get_real_x(), self.get_real_y())

    def move(self, screen, direction):
        """
        Move the player in the specific direction.
        """
        # self.rect.move_ip(*[d * self.speed for d in direction])
        self.world.set_offset(-1 * direction[0] * self.speed,
                              -1 * direction[1] * self.speed)

        # Add the negate value of dx and dy to the player position
        self.x = self.x - self.world.dx
        self.y = self.y - self.world.dy

        self.rotate(self.get_angle())
        self.animate(direction)

        # Update flashlight of player
        self.light.update(self.get_real_x(), self.get_real_y())

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
        # Keep the image on the same position.
        # Save its current center.
        x, y = self.rect.center
        # Replace old rect with new rect.
        self.rect = self.image.get_rect()
        # Put the new rect's center at old center.
        self.rect.center = (x, y)

    def animate(self, _direction):
        # Increase the image_index if there is a movement only
        if _direction[0] != 0 or _direction[1] != 0:
            # Move state
            self.movement_index = 1
        elif _direction[0] == 0 and _direction[1] == 0:
            # Idle state
            self.movement_index = 0

        if ((self.image_index + 1)
                < len(self.movement_images[self.movement_index])):
            self.image_index += 1
        else:
            self.image_index = 0
        # self.feets.move(direction)

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
    feet_offset_px = 0
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
                        image, (image.get_rect().width//2,
                                image.get_rect().height//2)))
                self.feet_images_orig.append(images_orig)
                self.feet_images.append(images)
            else:
                print('warn: Directory ' + directory + ' doesnt exists.')

        self.image = self.feet_images[self.feet_index][self.image_index]
        self.rect = self.image.get_rect()
        self.rect.center = (
            (self.player.get_x() - math.cos(self.player.angle) *
             self.feet_offset_px),
            (self.player.get_y() - math.sin(self.player.angle) *
             self.feet_offset_px))

    def move(self, direction):
        self.rect.center = (
            (self.player.get_x() - math.cos(self.player.angle) *
             self.feet_offset_px),
            (self.player.get_y() - math.sin(self.player.angle) *
             self.feet_offset_px))
        # Need to negate the result, if the image starts
        # at the wrong direction.
        self.image = pg.transform.rotate(
            self.feet_images[self.feet_index][self.image_index],
            (-1 * self.player.angle * (180 / math.pi)))
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

            if direction[1] > 0:
                # backward walk
                if (self.image_index - 1) > 0:
                    self.image_index -= 1
                else:
                    self.image_index = len(
                        self.feet_images[self.feet_index]) - 1
            else:
                if ((self.image_index + 1)
                        < len(self.feet_images[self.feet_index])):
                    self.image_index += 1
                else:
                    self.image_index = 0
        elif direction[0] == 0 and direction[1] == 0:
            # Idle state
            self.feet_index = 0
            self.image_index = 0
