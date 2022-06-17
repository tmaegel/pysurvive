#!/usr/bin/env python
# coding=utf-8
import math
import os

import pygame as pg

from .class_toolchain import Animation
from .config import IMAGE_DIR
from .utils import load_image


class Enemy(Animation):

    scale = 4
    speed = 2

    # Define the single movement states.
    # Each movement state is represented by a dictionary.
    movement_index = 0
    movements = [
        {
            "name": "idle",
        },
        {
            "name": "move",
        },
        {
            "name": "attack",
        },
    ]

    def __init__(self, _game, _x, _y):
        Animation.__init__(self)
        # Reference to the game instance.
        self.game = _game
        self.x = _x
        self.y = _y
        self.angle = math.pi

        self.path = None

        # for movement in self.movements:
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
        for movement in self.movements:
            _images = []
            directory = IMAGE_DIR + "zombie/" + movement["name"] + "/"
            if os.path.isdir(directory):
                path, _, files = next(os.walk(directory))
                for img in sorted(files):
                    if "spritesheet" not in img:
                        image, _ = load_image(path + img, alpha=True, path=False)
                        _images.append(
                            pg.transform.scale(
                                image,
                                (
                                    image.get_rect().width // self.scale,
                                    image.get_rect().height // self.scale,
                                ),
                            )
                        )
                self.images.append(_images)
            else:
                print("warn: Directory " + directory + " doesnt exists.")

        self.image = self.images[self.movement_index][0]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

        _offset = self.game.get_offset()
        self.rect.centerx = self.x - _offset[0]
        self.rect.centery = self.y - _offset[1]

    def update(self, dt, offset):
        """
        Update the enemy object.
        """

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
            self.frame %= len(self.images[self.movement_index])

            # Handle the different sprites for animation here
            self.animate()

        # @todo: Not time based yet
        # Update the position of the sprite.
        self.rect.centerx = round(self.x - offset[0])
        self.rect.centery = round(self.y - offset[1])

        # self.move()
        self.rotate(self.angle)

    def move(self) -> None:
        # Get the path to the player position.
        self.path = self.game.navmesh.get_astar_path(
            (self.x, self.y), (self.game.get_player_pos())
        )

        self.movement_index = 1
        # Get the move vector based in the angle
        _dx, _dy = self._get_move_vector(self.angle, self.speed)
        # Add the vector to the real position in the game world.
        self.x = round(self.x + _dx)
        self.y = round(self.y + _dy)
        # Update the position of the sprite for drawing.
        self.rect.centerx = round(self.rect.centerx + _dx)
        self.rect.centery = round(self.rect.centery + _dy)

    def rotate(self, angle) -> None:
        """
        Rotate the enemy object on the center.
        Need to negate the result, if the image starts
        at the wrong direction.

        :param angle: Rotation angle
        """
        self.image = pg.transform.rotate(
            self.images[self.movement_index][self.frame], (-1 * angle * (180 / math.pi))
        )
        # Recreating mask after every rotation
        self.mask = pg.mask.from_surface(self.image)
        # Keep the image on the same position.
        # Save its current center.
        x, y = self.rect.center
        # Replace old rect with new rect.
        self.rect = self.image.get_rect()
        # Put the new rect's center at old center.
        self.rect.center = (x, y)

    def attack(self) -> None:
        pass

    def animate(self) -> None:
        pass

    def _get_move_vector(self, angle, speed):
        return (math.cos(angle) * speed, math.sin(angle) * speed)
