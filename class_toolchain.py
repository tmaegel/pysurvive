import math
import pygame as pg


class Block(pg.sprite.Sprite):

    class BlockSegment():

        """
        Simple helper class to wrap all block segments (sides / line element)
        of the block (rectangle). So each block has 4 wall segments.
        """

        def __init__(self, _x1, _y1, _x2, _y2):
            self.x1 = _x1
            self.y1 = _y1
            self.x2 = _x2
            self.y2 = _y2

    def __init__(self, _x, _y, _width, _height, _xoffset, _yoffset):
        pg.sprite.Sprite.__init__(self)
        self.x = _x
        self.y = _y
        self.width = _width
        self.height = _height

        self.image = pg.Surface([self.width, self.height])
        self.image.fill((0, 0, 0))
        self.mask = pg.mask.from_surface(self.image)
        self.mask.fill()
        self.rect = self.image.get_rect()

        # Set the initial position for drawing only
        self.rect.x = self.x - _xoffset
        self.rect.y = self.y - _yoffset

        self.segments = []
        self.segments.append(
            self.BlockSegment(self.x, self.y,
                              self.x + self.width, self.y))
        self.segments.append(
            self.BlockSegment(self.x + self.width,
                              self.y, self.x + self.width,
                              self.y + self.height))
        self.segments.append(
            self.BlockSegment(self.x + self.width,
                              self.y + self.height, self.x,
                              self.y + self.height))
        self.segments.append(
            self.BlockSegment(self.x, self.y + self.height,
                              self.x, self.y))

    def update(self, _dx, _dy):
        # Update x, y position of the rect for drawing only
        self.rect.x = round(self.rect.x + _dx)
        self.rect.y = round(self.rect.y + _dy)

    def get_points(self):
        return ((self.x, self.y),
                (self.x + self.width, self.y),
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height))

    def get_center(self):
        return [self.x + self.width//2, self.y + self.height//2]


class Ray():

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

    def get_intersection(self, _walls, _closest=True):
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
        for wall in _walls:
            for segment in wall.segments:
                intersect = self.calc_intersection(segment)
                if not intersect:
                    continue
                if _closest:
                    if (not result_intersect or
                            intersect['param'] < result_intersect['param']):
                        result_intersect = intersect
                else:
                    if (not result_intersect or
                            intersect['param'] > result_intersect['param']):
                        result_intersect = intersect

        return result_intersect

    def calc_intersection(self, _segment):
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
        segment_dx = _segment.x2 - _segment.x1
        segment_dy = _segment.y2 - _segment.y1

        # Check if they are. If so, no intersect
        ray_mag = math.sqrt(dx * dx + dy * dy)
        segment_mag = math.sqrt(
            segment_dx * segment_dx + segment_dy * segment_dy)
        if (dx / ray_mag == segment_dx / segment_mag and
                dy / ray_mag == segment_dy / segment_mag):
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
            T2 = ((dx * (_segment.y1 - self.y0) +
                   dy * (self.x0 - _segment.x1)) /
                  (segment_dx * dy - segment_dy * dx))
            T1 = (_segment.x1 + segment_dx * T2 - self.x0) / dx
        except ZeroDivisionError:
            # print("warn: division by zero")
            return None

        # Must be within parametic whatevers for ray / segment
        if T1 < 0:
            return None
        if T2 < 0 or T2 > 1:
            return None

        # Return the point of intersection
        return {
            'x': int(self.x0 + dx * T1),
            'y': int(self.y0 + dy * T1),
            'param': T1
        }
