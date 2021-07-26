import os
import math
import pygame as pg

from config import (
    IMAGE_DIR,
)
from utils import load_image
from spritesheet import Spritesheet


class Enemy(pg.sprite.Sprite):

    speed = 4

    # Contains the scaled images
    images = []

    # Define the single movement states.
    # Each movement state is represented by a dictionary.
    # The speed attribute descripe the animation speed.
    # The next animation will be showed if the counter reach
    # the speed number.
    animation_counter = 0
    image_index = 0
    movement_index = 0
    movement_states = [
        {
            'name': 'idle',
            'speed': 1,
            'length': 17,
        },
        {
            'name': 'move',
            'speed': 1,
            'length': 17,
        },
        {
            'name': 'attack',
            'speed': 3,
            'length': 9,
        },
    ]

    def __init__(self, _game, _x, _y):
        # call Sprite initializer
        pg.sprite.Sprite.__init__(self)
        # Reference to the game object
        self.game = _game
        # Real position of the room in the game world
        self.x = _x
        self.y = _y

        # for movement in self.movement_states:
        #     _images = []
        #     _spritesheet = Spritesheet(
        #         IMAGE_DIR + 'zombie/' + movement['name'] + '/spritesheet.png')
        #     for i in range(movement['length']):
        #         sprite = _spritesheet.parse_sprite(i)
        #         _images.append(
        #             pg.transform.scale(sprite,
        #                                (sprite.get_rect().width//3,
        #                                 sprite.get_rect().height//3)))
        #     self.images.append(_images)

        # Preloading images
        for movement in self.movement_states:
            _images = []
            directory = IMAGE_DIR + 'zombie/' + movement['name'] + '/'
            if os.path.isdir(directory):
                path, _, files = next(os.walk(directory))
                for img in sorted(files):
                    if 'spritesheet' not in img:
                        image, _ = load_image(
                            path + img, alpha=True, path=False)
                        _images.append(pg.transform.scale(
                            image, (image.get_rect().width//3,
                                    image.get_rect().height//3)))
                self.images.append(_images)
            else:
                print('warn: Directory ' + directory + ' doesnt exists.')

        self.image = self.images[self.movement_index][self.image_index]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

        self.rect.centerx = self.x - self.game.x
        self.rect.centery = self.y - self.game.y

    def update(self):
        # Update x, y position of the rect for drawing only
        self.rect.centerx = round(self.rect.centerx + self.game.dx)
        self.rect.centery = round(self.rect.centery + self.game.dy)

        self.rotate(math.pi/3)

        # Handle the different sprites for animation here
        self.animate()

    def move(self):
        pass

    def rotate(self, _angle):
        """
        Rotate the enemy object on the center.
        Need to negate the result, if the image starts
        at the wrong direction.

        :param angle: Rotation angle
        """
        self.image = pg.transform.rotate(
            self.images[self.movement_index][self.image_index],
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

    def attack(self):
        pass

    def animate(self):
        def _switch_animation():
            self.animation_counter = 0
            if ((self.image_index + 1)
                    < len(self.images[self.movement_index])):
                self.image_index += 1
            else:
                self.image_index = 0

        if (self.animation_counter
                >= self.movement_states[self.movement_index]['speed']):
            _switch_animation()
        else:
            self.animation_counter += 1
