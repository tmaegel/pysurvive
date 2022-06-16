import math

import pygame as pg

from config import FPS


class Animation(pg.sprite.Sprite):
    def __init__(self):
        # call Sprite initializer
        pg.sprite.Sprite.__init__(self)
        # Contains a list of images/frames.
        self.images = []
        # Current image of the animation sequence/images.
        self.frame = 0
        # Next time it has to be updated in ms.
        self._next_update = 0
        # Frequency/period of the animation in ms.
        self._period = 1000.0 / FPS


class Screen(pg.sprite.Sprite):

    """
    Simple screen class to detect wheather objects
    are visible on the screen.
    """

    def __init__(self, _x, _y, _size):
        pg.sprite.Sprite.__init__(self)

        self.image = pg.Surface(_size)
        self.rect = self.image.get_rect()
        self.rect.x = _x
        self.rect.y = _y


class LineSegment:

    """
    Simple helper class to wrap all line segments (sides / line element)
    of the block. So each block has 4 line segments.
    """

    def __init__(self, _x1, _y1, _x2, _y2):
        self.x1 = _x1
        self.y1 = _y1
        self.x2 = _x2
        self.y2 = _y2

    def get_points(self):
        return ((self.x1, self.y1), (self.x2, self.y2))


class Block(pg.sprite.Sprite):

    """
    Simple helper class to wrap a block elments with x, y
    coordinates and width, height.
    """

    def __init__(
        self,
        _x,
        _y,
        _width,
        _height,
        _offset,
        _sides=("top", "right", "bottom", "left"),
    ):
        pg.sprite.Sprite.__init__(self)
        self.x = _x
        self.y = _y
        self.width = _width
        self.height = _height
        self.sides = _sides

        self.image = pg.Surface([self.width, self.height])
        self.mask = pg.mask.from_surface(self.image)
        self.mask.fill()
        self.rect = self.image.get_rect()

        # Set the initial position for drawing only
        self.rect.x = self.x - _offset[0]
        self.rect.y = self.y - _offset[1]

        # Add LineSegments (sides) of the block.
        self.segments = []
        if "top" in self.sides:
            self.segments.append(
                LineSegment(self.x, self.y, self.x + self.width, self.y)
            )
        if "right" in self.sides:
            self.segments.append(
                LineSegment(
                    self.x + self.width,
                    self.y,
                    self.x + self.width,
                    self.y + self.height,
                )
            )
        if "bottom" in self.sides:
            self.segments.append(
                LineSegment(
                    self.x,
                    self.y + self.height,
                    self.x + self.width,
                    self.y + self.height,
                )
            )
        if "left" in self.sides:
            self.segments.append(
                LineSegment(self.x, self.y, self.x, self.y + self.height)
            )

        # Points of the drawed line segments.
        self.points = ()
        for seg in self.segments:
            self.points += seg.get_points()

    def update(self, offset):
        # Update x, y position of the rect for drawing only.
        self.rect.x = round(self.x - offset[0])
        self.rect.y = round(self.y - offset[1])

    def get_points(self):
        return self.points

    def get_center(self):
        return [self.x + self.width // 2, self.y + self.height // 2]


class Ray:

    intersect = None

    def __init__(self, _x, _y, _angle):
        # x, y start coordinates of the ray.
        self.x0 = _x
        self.y0 = _y
        # Convert from -pi <-> pi to 0 <-> 2pi
        self.angle = (_angle + 2 * math.pi) % (2 * math.pi)
        # x, y coordinates of the ray that set the direction
        # on the ray based on the angle.
        self.x_dir = self.x0 + math.cos(self.angle)
        self.y_dir = self.y0 + math.sin(self.angle)

    def get_intersection(self, walls, closest=True):
        """
        Return the intersection of this ray and all wall segments.

        :param _walls: List of wall objects.
        :param _closest: If true returns the clostest intersect. If false
                         returns the farthest.
        :return: Return the x, y coordinates and a param that specified
                 the distance.
        :rtype: Dict
        """

        result_intersect = None
        for wall in walls:
            for segment in wall.segments:
                intersect = self.calc_intersection(segment)
                if not intersect:
                    continue
                if closest:
                    if (
                        not result_intersect
                        or intersect["param"] < result_intersect["param"]
                    ):
                        result_intersect = intersect
                else:
                    if (
                        not result_intersect
                        or intersect["param"] > result_intersect["param"]
                    ):
                        result_intersect = intersect

        return result_intersect

    def calc_intersection(self, segment):
        """
        Calculate the intersection with line segment and this ray.

        :param _segment: A line segment with two points.
        :return: Return the x, y coordinates and a param that specified
                 the distance.
        :rtype: Dict
        """

        # ray in parametric: point + direction * T1
        dx = self.x_dir - self.x0
        dy = self.y_dir - self.y0
        # segment in parametric: point + direction * T1
        segment_dx = segment.x2 - segment.x1
        segment_dy = segment.y2 - segment.y1

        # Check if they are. If so, no intersect
        ray_mag = math.sqrt(dx * dx + dy * dy)
        segment_mag = math.sqrt(segment_dx * segment_dx + segment_dy * segment_dy)
        if (
            dx / ray_mag == segment_dx / segment_mag
            and dy / ray_mag == segment_dy / segment_mag
        ):
            # Directions are the same.
            return None

        # solve for T1 and T2
        # ray.x1 + ray_dx * T1 = segment.x1 + segment_dx * T2
        # and
        # ray.y1 + ray_dy * T1 = segment.y1 + segment_dy * T2
        # ==> T1 = (segment.x1 + segment_dx * T2 - ray.x1) / ray_dx =
        #          (segment.y1 + segment_dy * T2 - ray.y1) / ray_dy
        # ==> segment.x1 * ray_dy
        #                + segment_dx * T2 * ray_dy - ray.x1 * ray_dy =
        #     segment.y1 * ray_dx
        #                + segment_dy * T2 * ray_dx - ray.y1 * ray_dx
        # ==> T2 = (ray_dx * (segment.y1 - ray.y1)
        #           + ray_dy * (ray.x1 - segment.x1)) /
        #          (segment_dx * ray_dy - segment_dy * ray_dx)
        try:
            T2 = (dx * (segment.y1 - self.y0) + dy * (self.x0 - segment.x1)) / (
                segment_dx * dy - segment_dy * dx
            )
            T1 = (segment.x1 + segment_dx * T2 - self.x0) / dx
        except ZeroDivisionError:
            # print("warn: division by zero")
            return None

        # Must be within parametic whatevers for ray / segment
        if T1 < 0:
            return None
        if T2 < 0 or T2 > 1:
            return None

        # Return the point of intersection
        return {"x": int(self.x0 + dx * T1), "y": int(self.y0 + dy * T1), "param": T1}
