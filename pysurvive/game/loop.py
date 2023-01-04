#!/usr/bin/env python
# coding=utf-8
import pygame as pg
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    QUIT,
)

from pysurvive.config import FPS, GRAY_LIGHT2, MAP_DIR, RED_LIGHT
from pysurvive.game.core import Camera, Screen
from pysurvive.logger import Logger
from pysurvive.map.level import Level
from pysurvive.player import PlayerGroup

logger = Logger()


class Game:

    running = True

    def __init__(self) -> None:
        logger.info("Starting...")
        pg.init()
        self.clock = pg.time.Clock()
        # Sprite that represent the screen.
        # Used to determine whether elements are in the viewing area.
        self.screen = Screen()
        # Set the height and width of the screen.
        self.window_surface = pg.display.set_mode(self.screen.size)
        # Set the window title.
        pg.display.set_caption("pysurvive")
        pg.transform.set_smoothscale_backend("SSE")
        # Turn off the mouse cursor.
        pg.mouse.set_visible(True)
        # Limit the number of allowed pygame events.
        # pg.event.set_allowed(
        #     [QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION]
        # )

        self.fps_font = pg.font.SysFont("Arial", 14)

        # Absolute (start) position of the player (camera) in game world.
        self.camera = Camera(300, 300)

        # Prepare the shadow surface / screen.
        # self.screen_shadow = pg.Surface(self.screen.size)
        # self.screen_shadow = self.screen_shadow.convert()
        # self.screen_shadow.set_alpha(240)
        # self.screen_shadow.set_colorkey(COLORKEY)

        #
        # Prepare game objects
        #

        # Initialize the navmesh based on the map.
        # self.navmesh = NavMesh(self)

        # self.enemy_sprites = pg.sprite.RenderPlain(
        #     Enemy(self, 100, 100),
        # )
        # A sprite group that contains all close enemy sprites (render only).
        # self.enemy_render_sprites = pg.sprite.RenderPlain()
        # A sprite group that contains all close sprites (collision only).
        # self.collide_sprites = pg.sprite.RenderPlain()

        # Get all unique points (corners) of block segments.
        # Prevent duplication of x, y coordinates.
        # self.unique_block_points = []
        # for block in self.block_sprites.sprites():
        #     for block_point in block.get_points():
        #         point = (block_point[0], block_point[1])
        #         if point not in self.unique_block_points:
        #             self.unique_block_points.append(point)

        # Map
        self.map_sprites = pg.sprite.RenderPlain((Level(f"{MAP_DIR}/map.json"),))
        # Player
        self.player_sprites = PlayerGroup()

    def start(self) -> None:
        """
        This function is called when the program starts. It initializes
        everything it needs, then runs in a loop until the function returns.
        """

        while self.running:

            # The number of milliseconds that passed between the
            # previous two calls to Clock.tick().
            dt = self.clock.get_time()

            for event in pg.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player_sprites.player.shot()
                    elif event.button == 3:
                        self.player_sprites.player.reload()
                elif event.type == MOUSEBUTTONUP:
                    pass

            keystate = pg.key.get_pressed()
            direction_x = keystate[pg.K_d] - keystate[pg.K_a]
            direction_y = keystate[pg.K_s] - keystate[pg.K_w]

            # Fill the window surface with the default background color.
            self.window_surface.fill(GRAY_LIGHT2)

            #
            # Updating
            #

            self.map_sprites.update()
            self.player_sprites.update(dt, (direction_x, direction_y))
            # Update all objects here otherwise the mechanism for
            # detecting which objects are on the screen is overridden.
            # self.enemy_sprites.update(dt, self.get_offset())

            #
            # Drawing
            #

            self.map_sprites.draw(self.window_surface)

            # if FLASHLIGHT_ENABLE:
            #     # Currently, all vertices within a virtual screen of
            #     # 3x width and 3x height of the screen are used. Later
            #     # when the visibility is limited, this can be further reduced.
            #     self.screen_shadow.fill(BLACK)
            #     self.player_sprites.light.draw(self.screen_shadow)
            #     self.window_surface.blit(self.screen_shadow, (0, 0))

            # self.block_render_sprites.draw(self.window_surface)
            self.player_sprites.draw(self.window_surface)
            # @todo: Do not draw all enemies later.
            # self.enemy_sprites.draw(self.window_surface)

            # Debugging
            # Draw navmesh
            # for tri in self.navmesh.mesh:
            #     triangle = [(p[0] - self.game_x, p[1] - self.game_y)
            #                 for p in tri.triangle]
            #     pg.draw.polygon(self.window_surface, (255, 0, 0), triangle, 1)
            #     for node in tri.nodes:
            #         pg.draw.circle(self.window_surface, (0, 255, 0),
            #                        (node.position[0] - self.game_x,
            #                         node.position[1] - self.game_y), 2)

            # path = self.enemy_sprites.sprites()[0].path
            # if path:
            #     path = [(p[0] - self.game_x, p[1] - self.game_y) for p in path]
            #     pg.draw.lines(self.window_surface, (0, 0, 255), False, path)

            self.window_surface.blit(self.update_fps(), (5, 5))

            # Go ahead and update the window surface with what we've drawn.
            # This MUST happen after all the other drawing commands.
            pg.display.flip()
            # This limits the while loop to a max of FPS times per second.
            self.clock.tick(FPS)

    def get_player_pos(self):
        return (self.player.x, self.player.y)

    # def get_block_points_on_screen(self):
    #     _block_points = []
    #     _offset = self.get_offset()
    #     _oversized_screen = pg.Rect(
    #         _offset[0] - self.screen.width,
    #         _offset[1] - self.screen.height,
    #         self.screen.width * 3,
    #         self.screen.height * 3,
    #     )
    #     for point in self.unique_block_points:
    #         if _oversized_screen.collidepoint(point):
    #             _block_points.append(point)
    #
    #     return _block_points

    def update_fps(self):
        fps = str(int(self.clock.get_fps()))
        fps_text = self.fps_font.render(fps, 1, RED_LIGHT)
        return fps_text
