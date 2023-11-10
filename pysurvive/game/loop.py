#!/usr/bin/env python
# coding=utf-8
import time

import pygame as pg
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    QUIT,
)

from pysurvive.config import FPS, GRAY_LIGHT2, MAP_DIR, SCREEN_RECT
from pysurvive.game.core import Camera
from pysurvive.logger import Logger
from pysurvive.map.level import Level
from pysurvive.player.player import PlayerGroup
from pysurvive.player.viewpoint import Viewpoint

logger = Logger()


class Game:
    running = True

    def __init__(self) -> None:
        logger.info("Starting...")
        pg.init()

        self.clock = pg.time.Clock()
        self.fps_font = pg.font.SysFont("Arial", 14)

        # Set the height and width of the camera/screen.
        self.window_surface = pg.display.set_mode(
            (SCREEN_RECT.width, SCREEN_RECT.height)
        )
        # Set the window title.
        pg.display.set_caption("pysurvive")
        pg.transform.set_smoothscale_backend("SSE")
        # Turn off the mouse cursor.
        pg.mouse.set_visible(False)
        # Limit the number of allowed pygame events.
        pg.event.set_allowed(
            [QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION]
        )

        self.camera = Camera()
        self.interface = pg.sprite.Group()

        self.level = Level(f"{MAP_DIR}/map.json")
        self.viewpoint = Viewpoint(self.interface)
        self.player_sprites = PlayerGroup(
            camera=self.camera,
            viewpoint=self.viewpoint,
        )

    def start(self) -> None:
        """
        This function is called when the program starts. It initializes
        everything it needs, then runs in a loop until the function returns.
        """

        prev_time = time.time()

        while self.running:
            # The number of milliseconds that passed between the
            # previous two calls to Clock.tick().
            dt = time.time() - prev_time
            prev_time = time.time()

            for event in pg.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.running = False
                elif event.type == MOUSEBUTTONUP:
                    pass

            # Default background color.
            self.window_surface.fill(GRAY_LIGHT2)

            #
            # Updating
            #

            self.level.update(self.camera)
            self.player_sprites.update(dt, self.level)
            self.interface.update()

            #
            # Drawing
            #

            self.level.draw(self.window_surface, self.camera)
            self.player_sprites.draw(self.window_surface, self.camera)
            self.interface.draw(self.window_surface)

            # Go ahead and update the window surface with what we've drawn.
            # This MUST happen after all the other drawing commands.
            pg.display.flip()
            # This limits the while loop to a max of FPS times per second.
            self.clock.tick(FPS)
