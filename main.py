import pygame as pg
from pygame.locals import (
    QUIT,
    K_ESCAPE,
    KEYDOWN,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
)

from config import (
    FPS,
    COLORKEY,
    BLACK,
    YELLOW,
    RED_LIGHT,
    SCREEN_RECT,
)
from class_toolchain import Screen
from navmesh import NavMesh
from room import Room, Box
from player import Player
from enemy import Enemy


class Game():

    running = True

    def __init__(self):
        pg.init()

        self.clock = pg.time.Clock()
        # Set the height and width of the screen
        self.screen = pg.display.set_mode(SCREEN_RECT.size)
        # Set the window title
        pg.display.set_caption('pysurvive')
        # Turn off the mouse cursor
        pg.mouse.set_visible(0)

        self.fps_font = pg.font.SysFont("Arial", 14)

        # Prepare the shadow surface / screeb
        self.screen_shadow = pg.Surface(self.screen.get_size())
        self.screen_shadow = self.screen_shadow.convert()
        self.screen_shadow.set_alpha(240)
        self.screen_shadow.set_colorkey(COLORKEY)

        # Absolute position of the game world
        self.player_start_x = 400
        self.player_start_y = 200
        # Fix offset for objects in the game world
        self.x = self.player_start_x - SCREEN_RECT.width//2
        self.y = self.player_start_y - SCREEN_RECT.height//2
        # Delta x, y for objects in the game world
        self.dx = 0.0
        self.dy = 0.0

        #
        # Prepare game objects
        #

        self.screen_sprite = Screen(SCREEN_RECT.size)

        # A sprite group that contains all room sprites
        self.room_sprites = pg.sprite.RenderPlain(
            Room(100, 100, 800, 600, ('left', 'right'), self.x, self.y),
            Room(-385, -100, 500, 1000, ('bottom', 'right'), self.x, self.y),
            Room(-385, 885, 500, 250, ('top'), self.x, self.y),
            Room(885, 200, 600, 400, ('left'), self.x, self.y),
        )
        # A sprite group that contains all wall sprites
        self.block_sprites = pg.sprite.RenderPlain(
            ((wall for wall in room.walls)
             for room in self.room_sprites.sprites()),
            Box(300, 300, 75, self.x, self.y)
        )
        self.enemy_sprites = pg.sprite.RenderPlain(
            Enemy(self, 1185, 400),
        )
        # A sprite group that contains all close room sprites (render only)
        self.room_render_sprites = pg.sprite.RenderPlain()
        # A sprite group that contains all close block sprites (render only)
        self.block_render_sprites = pg.sprite.RenderPlain()
        # A sprite group that contains all close enemy sprites (render only)
        self.enemy_render_sprites = pg.sprite.RenderPlain()
        # A sprite group that contains all close sprites (collision only)
        self.collide_sprites = pg.sprite.RenderPlain()

        # Get all unique points (corners) of block segments.
        # Prevent duplication of x, y coordinates.
        self.unique_block_points = []
        for block in self.block_sprites.sprites():
            for block_point in block.get_points():
                point = (block_point[0], block_point[1])
                if point not in self.unique_block_points:
                    self.unique_block_points.append(point)

        # Initialize the navmesh based on the map.
        self.navmesh = NavMesh(self)

        # Player
        self.player = Player(self, self.player_start_x, self.player_start_y)
        # A sprite group that contains all player sprites
        self.player_sprites = pg.sprite.RenderPlain(
            (self.player.feets, self.player))

    def start(self):
        """
        This function is called when the program starts.

        It initializes everything it needs, then runs in
        a loop until the function returns.
        """

        # Main loop
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
                        self.player.shot()
                    elif event.button == 3:
                        self.player.reload()
                elif event.type == MOUSEBUTTONUP:
                    pass

            keystate = pg.key.get_pressed()
            direction_x = keystate[pg.K_d] - keystate[pg.K_a]
            direction_y = keystate[pg.K_s] - keystate[pg.K_w]

            # Fill the screen with the default background color
            self.screen.fill(BLACK)

            #
            # Refactor the render sprites group
            #

            # Remove all sprites of the previous loop
            self.block_render_sprites.empty()
            self.room_render_sprites.empty()
            # Find the new sprites
            self.block_render_sprites.add(pg.sprite.spritecollide(
                self.screen_sprite, self.block_sprites, False,
                collided=pg.sprite.collide_rect))
            self.room_render_sprites.add(pg.sprite.spritecollide(
                self.screen_sprite, self.room_sprites, False,
                collided=pg.sprite.collide_rect))

            #
            # Updating
            #

            self.player_sprites.update([direction_x, direction_y], dt)
            # @todo: Update not all objects later
            self.enemy_sprites.update(dt)
            self.room_sprites.update(self.dx, self.dy)
            self.block_sprites.update(self.dx, self.dy)

            #
            # Drawing
            #

            self.room_render_sprites.draw(self.screen)

            # @todo: Do not use alle wall objects to
            # render/calculate the shadow
            self.screen_shadow.fill(BLACK)
            self.player.light.draw(self.screen_shadow)
            self.screen.blit(self.screen_shadow, (0, 0))

            self.block_render_sprites.draw(self.screen)
            if self.player.bullet:
                self.player.bullet.draw(self.screen, self.get_offset())
            self.player_sprites.draw(self.screen)
            self.enemy_sprites.draw(self.screen)

            pg.draw.line(self.screen, YELLOW,
                         (self.player.get_aim_x() - 5,
                          self.player.get_aim_y() - 5),
                         (self.player.get_aim_x() + 5,
                          self.player.get_aim_y() + 5))
            pg.draw.line(self.screen, YELLOW,
                         (self.player.get_aim_x() - 5,
                          self.player.get_aim_y() + 5),
                         (self.player.get_aim_x() + 5,
                          self.player.get_aim_y() - 5))

            # Debugging
            # Draw navmesh
            for tri in self.navmesh.mesh:
                triangle = [(p[0] - self.x, p[1] - self.y)
                            for p in tri.triangle]
                pg.draw.polygon(self.screen, (255, 0, 0), triangle, 1)
                for node in tri.nodes:
                    pg.draw.circle(self.screen, (0, 255, 0),
                                   (node.position[0] - self.x,
                                    node.position[1] - self.y), 2)

            self.path = self.navmesh.get_astar_path(
                (1185, 400), (self.player.get_x(), self.player.get_y()))
            self.path = [(p[0] - self.x, p[1] - self.y) for p in self.path]

            if self.path:
                pg.draw.lines(self.screen, (0, 0, 255), False, self.path)

            self.screen.blit(self.update_fps(), (5, 5))
            # Go ahead and update the screen with what we've drawn.
            # This MUST happen after all the other drawing commands.
            pg.display.flip()
            # This limits the while loop to a max of FPS times per second.
            self.clock.tick(FPS)

    def set_offset(self, _dx, _dy):
        self.dx = _dx
        self.dy = _dy
        self.x = round(self.x - _dx)
        self.y = round(self.y - _dy)

    def get_offset(self):
        return (self.x, self.y)

    def update_fps(self):
        fps = str(int(self.clock.get_fps()))
        fps_text = self.fps_font.render(fps, 1, RED_LIGHT)
        return fps_text


if __name__ == '__main__':
    game = Game()
    game.start()
