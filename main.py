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
    BLACK,
    SCREEN_RECT,
)

from world import World
from wall import Wall
from player import Player


if not pg.font:
    print('Warning, fonts disabled')
if not pg.mixer:
    print('Warning, sound disabled')


def main():
    """
    This function is called when the program starts.
    it initializes everything it needs, then runs in
    a loop until the function returns.
    """
    pg.init()
    # Set the height and width of the screen
    screen = pg.display.set_mode(SCREEN_RECT.size)
    # Set the window title
    pg.display.set_caption('pysurvive')
    # Turn off the mouse cursor
    # pg.mouse.set_visible(0)

    # Display the background
    # screen.blit(background, (0, 0))
    pg.display.flip()

    #
    # Prepare game objects
    #

    # World
    world = World()

    # Player
    player = Player(world)
    allsprites = pg.sprite.RenderPlain((player,))

    # Main Loop
    clock = pg.time.Clock()
    running = True
    while running:
        # This limits the while loop to a max of FPS times per second.
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                pass
            elif event.type == MOUSEBUTTONUP:
                pass

        # All drawing code happens after the for loop

        # Clear the screen and set the screen background
        screen.fill(BLACK)

        keystate = pg.key.get_pressed()
        direction_x = keystate[pg.K_d] - keystate[pg.K_a]
        direction_y = keystate[pg.K_s] - keystate[pg.K_w]
        player.move(screen, [direction_x, direction_y])

        # Sprite groups have an update() method,
        # which simply calls the update method for
        # all the sprites it contains
        allsprites.update()

        world.draw(screen)
        player.light.draw(screen)
        # Draw all sprites
        allsprites.draw(screen)

        # Go ahead and update the screen with what we've drawn.
        # This MUST happen after all the other drawing commands.
        pg.display.flip()


if __name__ == '__main__':
    main()
