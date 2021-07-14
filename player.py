import math
import pygame as pg

from config import (
    SCREEN_RECT,
)
from utils import load_image
from flashlight import Flashlight


class Player(pg.sprite.Sprite):

    speed = 4

    light = None

    def __init__(self, world):
        # call Sprite initializer
        pg.sprite.Sprite.__init__(self)

        self.image_original, _ = load_image('player/handgun/move/0.png')
        self.image_scaled = pg.transform.scale(self.image_original, (72, 72))
        self.image = self.image_original
        self.rect = self.image.get_rect(midbottom=SCREEN_RECT.midbottom)

        # Reference to the world object
        self.world = world

        # Store x and y position in extra variable because we need
        # floating accuracy.
        self.angle = 0
        self.angle_degree = -1 * self.angle * (180 / math.pi)

        # Initialize the light (flashlight) with x, y and angle from player
        self.light = Flashlight(
            self.get_pos_x(), self.get_pos_y(), self.angle, self.world)

    def move(self, screen, direction):
        """
        Move the player in the specific direction.
        """
        # Calculate the angel of the view based in the mouse position
        x = self.get_aim_x() - self.get_pos_x()
        y = self.get_aim_y() - self.get_pos_y()
        self.angle = (math.atan2(y, x) + 2 * math.pi) % (2 * math.pi)

        # Need to negate the result, if the image starts
        # at the wrong direction.
        self.angle_degree = -1 * self.angle * (180 / math.pi)
        self.image = pg.transform.rotate(
            self.image_scaled, self.angle_degree)
        # Keep the image on the same position.
        # Save its current center.
        x, y = self.rect.center
        # Replace old rect with new rect.
        self.rect = self.image.get_rect()
        # Put the new rect's center at old center.
        self.rect.center = (x, y)

        self.rect.move_ip(*[d * self.speed for d in direction])
        # Move to the left or to the right based on viewpoint
        # if direction_y < 0:
        #     self.x = self.x + math.cos(self.angle) * self.speed
        #     self.y = self.y + math.sin(self.angle) * self.speed
        # elif direction_y > 0:
        #     self.x = self.x - math.cos(self.angle) * self.speed
        #     self.y = self.y - math.sin(self.angle) * self.speed
        # # Move forward and backward based on the viewpoint
        # if direction_x < 0:
        #     self.x = self.x - math.cos(self.angle + math.pi / 2) * self.speed
        #     self.y = self.y - math.sin(self.angle + math.pi / 2) * self.speed
        # elif direction_x > 0:
        #     self.x = self.x + math.cos(self.angle + math.pi / 2) * self.speed
        #     self.y = self.y + math.sin(self.angle + math.pi / 2) * self.speed
        # self.rect.centerx = self.x
        # self.rect.centery = self.y

        # Update flashlight of player
        self.light.update(self.get_pos_x(), self.get_pos_y(), self.angle)

    def get_pos_x(self):
        return self.rect.centerx

    def get_pos_y(self):
        return self.rect.centery

    def get_aim_x(self):
        return pg.mouse.get_pos()[0]

    def get_aim_y(self):
        return pg.mouse.get_pos()[1]
