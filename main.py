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
    SCREEN_RECT,
)
from room import Room
from wall import Wall
from player import Player


class Game():

    running = True

    def __init__(self):
        pg.init()

        # Set the height and width of the screen
        self.screen = pg.display.set_mode(SCREEN_RECT.size)
        # Set the window title
        pg.display.set_caption('pysurvive')
        # Turn off the mouse cursor
        # pg.mouse.set_visible(0)

        # Prepare the shadow surface / screeb
        self.screen_shadow = pg.Surface(self.screen.get_size())
        self.screen_shadow = self.screen_shadow.convert()
        self.screen_shadow.set_alpha(240)
        self.screen_shadow.set_colorkey(COLORKEY)

        # Absolute position of the game world
        self.x = 0
        self.y = 0

        # Offset x, y for objects the game world
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
        self.wall_sprites = pg.sprite.RenderPlain(
            ((wall for wall in room.walls)
             for room in self.room_sprites.sprites())
        )
        # A sprite group that contains all close room sprites (render only)
        self.room_render_sprites = pg.sprite.RenderPlain()
        # A sprite group that contains all close wall sprites (render only)
        self.wall_render_sprites = pg.sprite.RenderPlain()
        # A sprite group that contains all close sprites (collision only)
        self.collide_sprites = pg.sprite.RenderPlain()

        # Get all unique points (corners) of wall segments.
        # Prevent duplication of x, y coordinates.
        self.unique_wall_points = []
        for wall in self.wall_sprites.sprites():
            for wall_point in wall.get_wall_points():
                point = (wall_point[0], wall_point[1])
                if point not in self.unique_wall_points:
                    self.unique_wall_points.append(point)

        # Player
        self.player = Player(self)
        # A sprite group that contains all player sprites
        self.player_sprites = pg.sprite.RenderPlain(
            (self.player,))

    def start(self):
        """
        This function is called when the program starts.
        it initializes everything it needs, then runs in
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
                    pass
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
            self.wall_render_sprites.empty()
            self.room_render_sprites.empty()
            # Find the new sprites
            self.wall_render_sprites.add(pg.sprite.spritecollide(
                self.screen_sprite, self.wall_sprites, False,
                collided=pg.sprite.collide_rect))
            self.room_render_sprites.add(pg.sprite.spritecollide(
                self.screen_sprite, self.room_sprites, False,
                collided=pg.sprite.collide_rect))

            #
            # Updating
            #

            self.player_sprites.update([direction_x, direction_y])
            # @todo: Update not all objects later
            self.room_sprites.update()
            self.wall_sprites.update()

            #
            # Drawing
            #

            self.room_render_sprites.draw(self.screen)

            # @todo: Do not use alle wall objects to render/calculate the shadow
            self.screen_shadow.fill(BLACK)
            self.player.light.draw(self.screen_shadow)
            self.screen.blit(self.screen_shadow, (0, 0))

            self.wall_render_sprites.draw(self.screen)
            self.player_sprites.draw(self.screen)

            # Go ahead and update the screen with what we've drawn.
            # This MUST happen after all the other drawing commands.
            pg.display.flip()
            # This limits the while loop to a max of FPS times per second.
            clock.tick(FPS)

    def set_offset(self, _dx, _dy):
        self.dx = _dx
        self.dy = _dy
        self.x = round(self.x + _dx)
        self.y = round(self.y + _dy)

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
