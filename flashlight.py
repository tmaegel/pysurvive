import math
import pygame as pg

from config import (
    GREEN,
    RED_LIGHT,
    GRAY_LIGHT,
    WHITE,
)


class Flashlight():

    light_rays = []

    def __init__(self, x0, y0, angle, world):
        self.x0 = x0
        self.y0 = y0
        # Initial angle (direction) of light.
        self.light_angle = angle
        # Range of flashlight, e.g. 90 degree.
        # From light_angle -45° and +45°
        self.light_range = math.pi / 4

        # Reference to the world object
        self.world = world

        # Get all unique points (corners) of wall segments.
        # Prevent duplication of x, y coordinates.
        self.unique_wall_points = []
        for wall in world.wall_segments:
            point1 = (wall.x1, wall.y1)
            point2 = (wall.x2, wall.y2)
            if point1 not in self.unique_wall_points:
                self.unique_wall_points.append(point1)
            if point2 not in self.unique_wall_points:
                self.unique_wall_points.append(point2)

    def update(self, x0, y0, angle):
        self.x0 = x0
        self.y0 = y0
        self.light_angle = angle

        ray1, ray2 = self._get_edge_rays()

        # For each (unique) line segment end point cast a ray directly towards
        # plus two more rays offset by +/- 0.00001 radians. The two extra rays
        # are needed to hit the wall(s) behind any given segment corner.
        unique_angles = [ray1.angle, ray2.angle]
        for point in self.unique_wall_points:
            # @todo: dict to tuple
            point = (point[0], point[1])
            # Build the triangle from x0, y0 (player position) and both
            # farthest intersections with the walls.
            triangle = ((ray1.x1, ray1.y1),
                        (ray1.intersect['x'], ray1.intersect['y']),
                        (ray2.intersect['x'], ray2.intersect['y']))
            # Consider points that are in the view only
            if self._is_point_in_view(point, triangle):
                angle = (math.atan2(
                    point[1] - self.y0,
                    point[0] - self.x0)
                    + 2 * math.pi) % (2 * math.pi)
                unique_angles.append(angle-0.00001)
                unique_angles.append(angle)
                unique_angles.append(angle+0.00001)

        self.light_rays = []
        # With the resulting angles we can now calculate the intersection
        # between wall and light ray.
        for angle in unique_angles:
            light_ray = LightRay(self.x0, self.y0, angle)
            light_ray.intersect = self._get_intersection(light_ray)
            self.light_rays.append(light_ray)

        # Sort the rays by angle
        self.light_rays.sort(key=lambda x: x.angle)

    def _get_intersection(self, ray, closest=True):
        """
        Return the intersection of a specific ray and all wall segments.

        :param ray: The ray object
        :param clostest: If true returns the clostest intersect. If false
                         returns the farthest.
        :return: Return the x, y coordinates and a param that specified
                 the distance.
        :rtype: Dict
        """
        result_intersect = None
        for wall in self.world.wall_segments:
            intersect = self._calc_intersection(ray, wall)
            if not intersect:
                continue
            if closest:
                if (not result_intersect or
                        intersect['param'] < result_intersect['param']):
                    result_intersect = intersect
            else:
                if (not result_intersect or
                        intersect['param'] > result_intersect['param']):
                    result_intersect = intersect

        return result_intersect

    def _calc_intersection(self, ray, wall):
        # raylight in parametric: point + direction * T1
        ray_dx = ray.x2 - ray.x1
        ray_dy = ray.y2 - ray.y1

        # wall in parametric: point + direction * T1
        wall_dx = wall.x2 - wall.x1
        wall_dy = wall.y2 - wall.y1

        # Check if they are. If so, no intersect
        ray_mag = math.sqrt(ray_dx * ray_dx + ray_dy * ray_dy)
        wall_mag = math.sqrt(wall_dx * wall_dx + wall_dy * wall_dy)
        if (ray_dx / ray_mag == wall_dx / wall_mag and
                ray_dy / ray_mag == wall_dy / wall_mag):
            # Directions are the same.
            return None

        # solve for T1 and T2
        # ray.x1 + ray_dx * T1 = wall.x1 + wall_dx * T2
        # and
        # ray.y1 + ray_dy * T1 = wall.y1 + wall_dy * T2
        # ==> T1 = (wall.x1 + wall_dx * T2 - ray.x1) / ray_dx =
        #          (wall.y1 + wall_dy * T2 - ray.y1) / ray_dy
        # ==> wall.x1 * ray_dy + wall_dx * T2 * ray_dy - ray.x1 * ray_dy =
        #     wall.y1 * ray_dx + wall_dy * T2 * ray_dx - ray.y1 * ray_dx
        # ==> T2 = (ray_dx * (wall.y1 - ray.y1)
        #           + ray_dy * (ray.x1 - wall.x1)) /
        #          (wall_dx * ray_dy - wall_dy * ray_dx)
        try:
            T2 = ((ray_dx * (wall.y1 - ray.y1) +
                   ray_dy * (ray.x1 - wall.x1)) /
                  (wall_dx * ray_dy - wall_dy * ray_dx))
            T1 = (wall.x1 + wall_dx * T2 - ray.x1) / ray_dx
        except ZeroDivisionError:
            # print("warn: division by zero")
            return None

        # Must be within parametic whatevers for ray / wall
        if T1 < 0:
            return None
        if T2 < 0 or T2 > 1:
            return None

        # Return the point of intersection
        return {
            'x': int(ray.x1 + ray_dx * T1),
            'y': int(ray.y1 + ray_dy * T1),
            'param': T1
        }

    def _get_edge_rays(self):
        """
        To limit the field of view / flashlight the edge rays are needed.
        To calculate the endpositions of the rays the farthest intersection
        will be calculated. These should be the intersections with the
        outermost walls. Here the rays will be extended so that the
        resulting triangle (position player and endpoints of the rays)
        can be used for calculation.

        :return ray1: First edge ray
        :return ray2: Second edge ray
        :rtype: Object LightRay
        """
        ray1 = LightRay(
            self.x0, self.y0, self.light_angle + self.light_range / 2)
        ray1.intersect = self._get_intersection(ray1, closest=False)
        ray1.intersect['x'] = int(
            (ray1.intersect['x'] + math.cos(ray1.angle) * 1000))
        ray1.intersect['y'] = int(
            (ray1.intersect['y'] + math.sin(ray1.angle) * 1000))

        ray2 = LightRay(
            self.x0, self.y0, self.light_angle - self.light_range / 2)
        ray2.intersect = self._get_intersection(ray2, closest=False)
        ray2.intersect['x'] = int(
            (ray2.intersect['x'] + math.cos(ray2.angle) * 1000))
        ray2.intersect['y'] = int(
            (ray2.intersect['y'] + math.sin(ray2.angle) * 1000))

        return ray1, ray2

    def _is_point_in_view(self, point, triangle):
        """
        Returns True if the point is inside the triangle and returns False
        if it falls outside.

        :param point: is a tuple with two elements containing the
                      x, y coordinates respectively.
        :param triangle: is a tuple with three elements each element
                         consisting of a tuple of x, y coordinates.

        It works like this:
        Walk clockwise or counterclockwise around the triangle and
        project the point onto the segment we are crossing by using
        the dot product. Finally, check that the vector created is
        on the same side for each of the triangle's segments.
        """
        # Unpack arguments
        x, y = point
        ax, ay = triangle[0]
        bx, by = triangle[1]
        cx, cy = triangle[2]
        # Segment A to B
        side_1 = (x - bx) * (ay - by) - (ax - bx) * (y - by)
        # Segment B to C
        side_2 = (x - cx) * (by - cy) - (bx - cx) * (y - cy)
        # Segment C to A
        side_3 = (x - ax) * (cy - ay) - (cx - ax) * (y - ay)

        # All the signs must be positive or all negative
        return (side_1 < 0.0) == (side_2 < 0.0) == (side_3 < 0.0)

    def _get_light_polygon(self):
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
        init_ray = None
        ray_prev = None
        for i, ray in enumerate(self.light_rays):
            if i == 0:
                init_ray = ray
                polygon.append([ray.intersect['x'], ray.intersect['y']])
            else:
                if abs(ray.angle - ray_prev.angle) > self.light_range:
                    polygon.append([self.x0, self.y0])

                if ray.intersect:
                    polygon.append(
                        [ray.intersect['x'], ray.intersect['y']])
                # else:
                #     print("warn: no point added to light polygon.")

            ray_prev = ray

        if [self.x0, self.y0] in polygon:
            polygon.append(
                [init_ray.intersect['x'], init_ray.intersect['y']])
        else:
            polygon.append([self.x0, self.y0])

        return polygon

    def draw(self, screen):
        polygon = self._get_light_polygon()
        if len(polygon) > 2:
            pg.draw.polygon(screen, WHITE, polygon)


class LightRay():

    def __init__(self, x1, y1, angle):
        self.x1 = y1
        self.y1 = y1
        # Convert from -pi <-> pi to 0 <-> 2pi
        self.angle = (angle + 2 * math.pi) % (2 * math.pi)
        self.intersect = None

        self.update(x1, y1)

    def update(self, x, y):
        self.x1 = x
        self.y1 = y
        self.x2 = self.x1 + math.cos(self.angle)
        self.y2 = self.y1 + math.sin(self.angle)

    def draw(self, screen):
        if self.intersect:
            pg.draw.line(screen, RED_LIGHT,
                         (self.x1, self.y1),
                         (self.intersect['x'], self.intersect['y']))
            pg.draw.circle(screen, RED_LIGHT,
                           [self.intersect['x'], self.intersect['y']], 4)
