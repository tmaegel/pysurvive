import pygame as pg

from utils import load_image
from wall import Wall


class World():

    wall_width = 25

    def __init__(self):

        # Absolute position of the world
        self.x = 0
        self.y = 0
        # Offset x, y for objects the world
        self.dx = 0
        self.dy = 0

        self.rooms = [
            Room(self, 100, 100, 800, 600, 'textures/stone_floor1.png'),
            Room(self, -300, -100, 400, 600, 'textures/stone_floor2.png')
        ]

        self.walls = [
            # Room 1
            Wall(self, 100, 100, 800, self.wall_width),
            Wall(self, 100 + 800 - self.wall_width, 100 + \
                 self.wall_width, self.wall_width, 600 - self.wall_width * 2),
            Wall(self, 100, 100 + 600 - self.wall_width,
                 800, self.wall_width),
            Wall(self, 100, 100 + self.wall_width,
                 self.wall_width, 100 - self.wall_width),
            Wall(self, 100, 350, self.wall_width, 350 - self.wall_width),
            Wall(self, 400 - self.wall_width//2, 250, self.wall_width, 300),
            # Room 2
            Wall(self, -300, -100, 400, self.wall_width),
            Wall(self, -300 + 400 - self.wall_width, -100, self.wall_width,
                 300),
            Wall(self, -300, -100 + 600 - self.wall_width, 400,
                 self.wall_width),
            Wall(self, -300, -100, self.wall_width, 600),
        ]

        # Get all unique points (corners) of wall segments.
        # Prevent duplication of x, y coordinates.
        self.unique_wall_points = []
        for wall in self.walls:
            for wall_point in wall.get_wall_points():
                point = (wall_point[0], wall_point[1])
                if point not in self.unique_wall_points:
                    self.unique_wall_points.append(point)

    def draw(self, screen):
        # Draw the wall segments here
        for wall in self.walls:
            wall.draw(screen)

    def set_offset(self, _dx, _dy):
        self.dx = _dx
        self.dy = _dy
        self.x += _dx
        self.y += _dy

    def get_offset(self):
        return (self.x, self.y)


class Room(pg.sprite.Sprite):

    scale_px = 256

    def __init__(self, _world, _x, _y, _width, _height, _texture):
        pg.sprite.Sprite.__init__(self)

        self.world = _world
        # Real position of the room in the world
        self.x = _x
        self.y = _y
        self.width = _width
        self.height = _height

        self.image = pg.Surface([self.width, self.height])
        self.rect = self.image.get_rect()

        # Set position for drawing only
        self.rect.x = self.x
        self.rect.y = self.y

        self.texture_orig, _ = load_image(_texture)
        self.texture = pg.transform.scale(
            self.texture_orig, (self.scale_px, self.scale_px))
        for x in range(0, self.rect.width, self.scale_px):
            for y in range(0, self.rect.height, self.scale_px):
                self.image.blit(self.texture, (x, y))

    def update(self):
        # Update x, y position of the rect for drawing only
        self.rect.x += self.world.dx
        self.rect.y += self.world.dy
