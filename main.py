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
    GRAY_LIGHT,
    YELLOW,
    SCREEN_RECT,
)
from room import Room, Box
from player import Player
from enemy import Enemy


class Game():

    running = True

    def __init__(self):
        pg.init()

        # Set the height and width of the screen
        self.screen = pg.display.set_mode(SCREEN_RECT.size)
        # Set the window title
        pg.display.set_caption('pysurvive')
        # Turn off the mouse cursor
        pg.mouse.set_visible(0)

        # Prepare the shadow surface / screeb
        self.screen_shadow = pg.Surface(self.screen.get_size())
        self.screen_shadow = self.screen_shadow.convert()
        self.screen_shadow.set_alpha(240)
        self.screen_shadow.set_colorkey(COLORKEY)

        # Absolute position of the game world
        self.player_start_x = 500
        self.player_start_y = 400
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
            Room(self, 100, 100, 800, 600, ('left', 'right')),
            Room(self, -385, -100, 500, 1000, ('bottom', 'right')),
            Room(self, -385, 885, 500, 250, ('top')),
            Room(self, 885, 200, 600, 400, ('left')),
        )
        # A sprite group that contains all wall sprites
        self.block_sprites = pg.sprite.RenderPlain(
            ((wall for wall in room.walls)
             for room in self.room_sprites.sprites()),
            Box(self, 300, 300, 75)
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
        clock = pg.time.Clock()
        while self.running:
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

            self.player_sprites.update([direction_x, direction_y])
            # @todo: Update not all objects later
            self.enemy_sprites.update()
            self.room_sprites.update()
            self.block_sprites.update()

            #
            # Drawing
            #

            self.room_render_sprites.draw(self.screen)

            # @todo: Do not use alle wall objects to render/calculate the shadow
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

            # Go ahead and update the screen with what we've drawn.
            # This MUST happen after all the other drawing commands.
            pg.display.flip()
            # This limits the while loop to a max of FPS times per second.
            clock.tick(FPS)

    def set_offset(self, _dx, _dy):
        self.dx = _dx
        self.dy = _dy
        self.x = round(self.x - _dx)
        self.y = round(self.y - _dy)

    def get_offset(self):
        return (self.x, self.y)


class Screen(pg.sprite.Sprite):

    """
    Simple screen class to detect wheather objects
    are visible on the screen.
    """

    def __init__(self, _size):
        pg.sprite.Sprite.__init__(self)

        self.image = pg.Surface(_size)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0


if __name__ == '__main__':
    game = Game()
    game.start()