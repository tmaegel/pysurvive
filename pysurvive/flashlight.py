#!/usr/bin/env python
# coding=utf-8
import math

import pygame as pg

from .class_toolchain import Ray
from .config import COLORKEY, RED_LIGHT


class Flashlight:

    rays = []  # type: ignore

    def __init__(self, _player, _x0, _y0):
        self.player = _player
        self.x0 = _x0
        self.y0 = _y0

        self.update(_x0, _y0)

    def update(self, _x0, _y0):
        self.x0 = _x0
        self.y0 = _y0

        # Update the single rays of the current view
        self.rays = self._get_sight_rays(self.x0, self.y0)
        for ray in self.rays:
            ray.update(self.x0, self.y0)

    def _get_sight_rays(self, _x0, _y0):
        """
        Returns a list with all rays towards to the unique block points
        and within the player vision range based on x0 and y0.

        :return rays: List of rays
        :rtype: List
        """
        rays = []
        # ray1, ray2 = self._get_edge_rays(_x0, _y0)

        # For each (unique) line segment end point cast a ray directly towards
        # plus two more rays offset by +/- 0.00001 radians. The two extra rays
        # are needed to hit the wall/block(s) behind any given segment corner.
        # unique_angles = [ray1.angle, ray2.angle]
        unique_angles = []
        for point in self.player.game.get_block_points_on_screen():
            # point = (point[0], point[1])
            # Build the triangle from x0, y0 (player position) and both
            # farthest intersections with the walls.
            # triangle = ((_x0, _y0),
            #             (ray1.intersect['x'], ray1.intersect['y']),
            #             (ray2.intersect['x'], ray2.intersect['y']))
            # Consider points that are in the view only
            # if self._is_point_in_view(point, triangle):
            angle = (math.atan2(point[1] - _y0, point[0] - _x0) + 2 * math.pi) % (
                2 * math.pi
            )
            unique_angles.append(angle - 0.00001)
            unique_angles.append(angle)
            unique_angles.append(angle + 0.00001)

        # With the resulting angles we can now calculate the intersection
        # between block and ray.
        for angle in unique_angles:
            ray = LightRay(_x0, _y0, angle)
            ray.intersect = ray.get_intersection(
                self.player.game.block_sprites.sprites()
            )
            if ray.intersect:
                rays.append(ray)

        # Sort the rays by angle
        rays.sort(key=lambda x: x.angle)

        return rays

    # def _get_edge_rays(self, _x0, _y0):
    #     """
    #     To limit the field of view / flashlight the edge rays are needed.
    #     To calculate the endpositions of the rays the farthest intersection
    #     will be calculated. These should be the intersections with the
    #     outermost walls. Here the rays will be extended so that the
    #     resulting triangle (position player and endpoints of the rays)
    #     can be used for calculation.

    #     :return ray1: First edge ray
    #     :return ray2: Second edge ray
    #     :rtype: Object LightRay
    #     """
    #     ray1 = LightRay(
    #         _x0, _y0, self.light_angle + self.light_range / 2)
    #     ray1.intersect = self._get_intersection(ray1, closest=False)
    #     ray1.intersect['x'] = int(
    #         (ray1.intersect['x'] + math.cos(ray1.angle) * 1000))
    #     ray1.intersect['y'] = int(
    #         (ray1.intersect['y'] + math.sin(ray1.angle) * 1000))

    #     ray2 = LightRay(
    #         _x0, _y0, self.light_angle - self.light_range / 2)
    #     ray2.intersect = self._get_intersection(ray2, closest=False)
    #     ray2.intersect['x'] = int(
    #         (ray2.intersect['x'] + math.cos(ray2.angle) * 1000))
    #     ray2.intersect['y'] = int(
    #         (ray2.intersect['y'] + math.sin(ray2.angle) * 1000))

    #     return ray1, ray2

    # def _is_point_in_view(self, _point, _triangle):
    #     """
    #     Returns True if the point is inside the triangle and returns False
    #     if it falls outside.

    #     :param point: is a tuple with two elements containing the
    #                   x, y coordinates respectively.
    #     :param triangle: is a tuple with three elements each element
    #                      consisting of a tuple of x, y coordinates.

    #     It works like this:
    #     Walk clockwise or counterclockwise around the triangle and
    #     project the point onto the segment we are crossing by using
    #     the dot product. Finally, check that the vector created is
    #     on the same side for each of the triangle's segments.
    #     """
    #     # Unpack arguments
    #     x, y = _point
    #     ax, ay = _triangle[0]
    #     bx, by = _triangle[1]
    #     cx, cy = _triangle[2]
    #     # Segment A to B
    #     side_1 = (x - bx) * (ay - by) - (ax - bx) * (y - by)
    #     # Segment B to C
    #     side_2 = (x - cx) * (by - cy) - (bx - cx) * (y - cy)
    #     # Segment C to A
    #     side_3 = (x - ax) * (cy - ay) - (cx - ax) * (y - ay)

    #     # All the signs must be positive or all negative
    #     return (side_1 < 0.0) == (side_2 < 0.0) == (side_3 < 0.0)

    def _get_sight_polygon(self, _rays):
        """
        This returns a list with all points represented the view (flashlight).

        In some cases, the start and end point of the polygon must be varied.
        This becomes necessary when the individual rays of light are in the
        first as well as 4 quadrants. By modifying the start or end point,
        the points of the polygon are drawn in the correct order.

        :return polygon: List of points of the view (flashlight).
        :rtype: List
        """
        polygon = []
        # append_origin = False
        # init_ray = None
        # ray_prev = None
        # for i, ray in enumerate(_rays):
        #     if i == 0:
        #         init_ray = ray
        #         polygon.append((ray.intersect['x'], ray.intersect['y']))
        #     else:
        #         if abs(ray.angle - ray_prev.angle) > self.light_range:
        #             polygon.append((self.x0, self.y0))
        #             append_origin = True
        #         polygon.append(
        #             (ray.intersect['x'], ray.intersect['y']))

        #     ray_prev = ray

        # if append_origin:
        #     polygon.append(
        #         (init_ray.intersect['x'], init_ray.intersect['y']))
        # else:
        #     polygon.append((self.x0, self.y0))

        for ray in _rays:
            polygon.append(
                (
                    ray.intersect["x"] - self.player.game.get_offset()[0],
                    ray.intersect["y"] - self.player.game.get_offset()[1],
                )
            )

        return polygon

    def draw(self, screen):

        # fuzzy_radius = 20
        # angle = 0
        # polygons = []
        # while angle < (math.pi * 2):
        #     dx = math.cos(angle) * fuzzy_radius
        #     dy = math.sin(angle) * fuzzy_radius
        #     polygons.append(self._get_sight_rays(self.x0 + dx, self.y0 + dy))
        #     angle += math.pi * 2 / 10

        # c = 10
        # for p in polygons:
        #     # c += 10
        #     p_shadow = self._get_sight_polygon(p)
        #     if len(p_shadow) > 2:
        #         pg.draw.polygon(screen, (c, c, c), p_shadow)

        # Draw the sight polygon and the view circle
        polygon = self._get_sight_polygon(self.rays)
        if len(polygon) > 2:
            pg.draw.polygon(screen, COLORKEY, polygon)

        # for ray in self.rays:
        #     ray.draw(screen,
        #              self.player.get_virt_x(),
        #              self.player.get_virt_y(),
        #              self.player.game.get_offset())


class LightRay(Ray):
    def __init__(self, _x, _y, _angle):
        Ray.__init__(self, _x, _y, _angle)

    def update(self, _x, _y):
        # x, y start coordinates of the ray.
        self.x0 = _x
        self.y0 = _y
        # x, y coordinates of the ray that set the direction.
        self.x_dir = self.x0 + math.cos(self.angle)
        self.y_dir = self.y0 + math.sin(self.angle)

    def draw(self, screen, _x, _y, _offset):
        """
        Draw the individual light rays.
        The virtual x and y coordinates are passed to the player objects.
        This is necessary because of the scolling of the game world.
        By scrolling the game world, the objects (e.g. segments) are moved
        virtually (only when drawing). The virtual position of the player
        is always in the center of the screen.
        In addition, an offset (x, y) of the game world is passed so that
        the intersection points with these are also moved.
        """

        if self.intersect:
            pg.draw.line(
                screen,
                RED_LIGHT,
                (_x, _y),
                (self.intersect["x"] - _offset[0], self.intersect["y"] - _offset[1]),
            )
            pg.draw.circle(
                screen,
                RED_LIGHT,
                (self.intersect["x"] - _offset[0], self.intersect["y"] - _offset[1]),
                4,
            )
