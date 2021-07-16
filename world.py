from config import (
    SCREEN_RECT,
)
from wall import Wall


class World():

    def __init__(self):
        self.walls = [
            # border
            Wall(0, 0, SCREEN_RECT.width, 10),
            Wall(SCREEN_RECT.width - 10, 0, 10, SCREEN_RECT.height),
            Wall(0, SCREEN_RECT.height - 10, SCREEN_RECT.width, 10),
            Wall(0, 0, 10, SCREEN_RECT.height),

            Wall(150, 150, 10, 100),
            Wall(150, 518, 10, 100),
            Wall(874, 150, 10, 100),
            Wall(874, 518, 10, 100),
            Wall(507, 334, 10, 100),
        ]
        self.unique_wall_points = []

        # Get all unique points (corners) of wall segments.
        # Prevent duplication of x, y coordinates.
        for wall in self.walls:
            for wall_point in wall.get_wall_points():
                point = (wall_point[0], wall_point[1])
                if point not in self.unique_wall_points:
                    self.unique_wall_points.append(point)

    def draw(self, screen):
        # Draw the wall segments here
        for wall in self.walls:
            wall.draw(screen)
