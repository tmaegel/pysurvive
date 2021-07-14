from config import (
    SCREEN_RECT,
)
from wall import Wall


class World():

    def __init__(self):
        self.wall_segments = [
            # border
            Wall(0, 0, SCREEN_RECT.width - 1, 0),
            Wall(SCREEN_RECT.width - 1, 0,
                 SCREEN_RECT.width - 1, SCREEN_RECT.height - 1),
            Wall(SCREEN_RECT.width - 1,
                 SCREEN_RECT.height - 1, 0, SCREEN_RECT.height - 1),
            Wall(0, SCREEN_RECT.height - 1, 0, 0),

            # segments 1
            Wall(100, 150, 120, 50),
            Wall(120, 50, 200, 80),
            Wall(200, 80, 140, 210),
            Wall(140, 210, 100, 150),

            # segment 2
            Wall(700, 200, 720, 250),
            Wall(720, 250, 660, 300),
            Wall(660, 300, 700, 200),

            # segment 3
            Wall(200, 460, 220, 550),
            Wall(220, 550, 300, 500),
            Wall(300, 500, 350, 420),
            Wall(350, 420, 200, 460),

            # segment 4
            Wall(340, 60, 360, 40),
            Wall(360, 40, 370, 70),
            Wall(370, 70, 340, 60),

            # segment 5
            Wall(450, 190, 560, 170),
            Wall(560, 170, 540, 270),
            Wall(540, 270, 430, 290),
            Wall(430, 290, 450, 190),

            # segment 6
            Wall(520, 495, 720, 450),
            Wall(720, 450, 680, 550),
            Wall(680, 550, 520, 495),
        ]

    def update(self):
        pass

    def draw(self, screen):
        # Draw the wall segments here
        for wall in self.wall_segments:
            wall.draw(screen)
