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
    WHITE,
    SCREEN_RECT,
)

from utils import load_image

from world import World
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

    # Prepare the background surface / screen
    screen_bg = pg.Surface(screen.get_size())
    screen_bg = screen_bg.convert()
    bg_image, _ = load_image('textures/stone_floor1.png', alpha=True)
    bg_image = pg.transform.scale(bg_image, (256, 256))
    bg_width = bg_image.get_size()[0]
    bg_height = bg_image.get_size()[1]
    for x in range(SCREEN_RECT.width // bg_width + 1):
        for y in range(SCREEN_RECT.height // bg_height + 1):
            screen_bg.blit(bg_image, (x * bg_width, y * bg_height))
    screen.blit(screen_bg, (0, 0))

    # Prepare the shadow surface / screeb
    screen_shadow = pg.Surface(screen.get_size())
    screen_shadow = screen_shadow.convert()
    screen_shadow.set_alpha(220)
    screen_shadow.set_colorkey(WHITE)

    #
    # Prepare game objects
    #

    # World
    world = World()

    # Player
    player = Player(world)
    allsprites = pg.sprite.RenderPlain((player,))

    # Main loop
    clock = pg.time.Clock()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                pass
            elif event.type == MOUSEBUTTONUP:
                pass

        #
        # All drawing code happens after the for loop
        #

        screen.blit(screen_bg, (0, 0))

        screen_shadow.fill(BLACK)
        player.light.draw(screen_shadow)
        screen.blit(screen_shadow, (0, 0))

        keystate = pg.key.get_pressed()
        direction_x = keystate[pg.K_d] - keystate[pg.K_a]
        direction_y = keystate[pg.K_s] - keystate[pg.K_w]
        player.move(screen, [direction_x, direction_y])

        # Sprite groups have an update() method,
        # which simply calls the update method for
        # all the sprites it contains
        allsprites.update()

        # Draw all sprites
        allsprites.draw(screen)

        world.draw(screen)

        # Go ahead and update the screen with what we've drawn.
        # This MUST happen after all the other drawing commands.
        pg.display.flip()
        # This limits the while loop to a max of FPS times per second.
        clock.tick(FPS)


if __name__ == '__main__':
    main()
