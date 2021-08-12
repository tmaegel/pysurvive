import random
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
    BLUE,
    RED_LIGHT,
    GRAY_LIGHT2,
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
        # Set the height and width of the screen.
        self.screen = pg.display.set_mode(SCREEN_RECT.size)
        # Set the window title.
        pg.display.set_caption('pysurvive')
        # Turn off the mouse cursor.
        pg.mouse.set_visible(0)
        # Limit the number of allowed pygame events.
        pg.event.set_allowed(
            [QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

        self.fps_font = pg.font.SysFont("Arial", 14)

        # Prepare the shadow surface / screen.
        self.screen_shadow = pg.Surface(self.screen.get_size())
        self.screen_shadow = self.screen_shadow.convert()
        self.screen_shadow.set_alpha(240)
        self.screen_shadow.set_colorkey(COLORKEY)

        # Absolute position of the game world.
        self.player_start_x = 200
        self.player_start_y = 200
        # Global game position. Offset for objects in the game world.
        self.game_x = self.player_start_x - SCREEN_RECT.width//2
        self.game_y = self.player_start_y - SCREEN_RECT.height//2

        #
        # Prepare game objects
        #

        # Used to determine whether elements are in the viewing area.
        self.screen_sprite = Screen(0, 0, SCREEN_RECT.size)

        # A sprite group that contains all room sprites..
        self.room_sprites = pg.sprite.RenderPlain(
            self.create_rooms()
            # Room(100, 100, 800, 600, self.get_offset(),
            #      _doors=('right', 'left')),
            # Room(-400, -100, 500, 1000, self.get_offset(),
            #      _doors=('bottom', 'right')),
            # Room(-400, 900, 500, 250, self.get_offset(), _doors=('top')),
            # Room(900, 200, 600, 400, self.get_offset(), _doors=('left')),
        )

        # A sprite group that contains all wall and block sprites.
        self.block_sprites = pg.sprite.RenderPlain(
            ((wall for wall in room.walls)
             for room in self.room_sprites.sprites()),
            # Box(350, 325, 75, self.get_offset())
        )

        # Initialize the navmesh based on the map.
        self.navmesh = NavMesh(self)

        self.enemy_sprites = pg.sprite.RenderPlain(
            # Enemy(self, 1150, 400),
        )
        # A sprite group that contains all close room sprites (render only).
        self.room_render_sprites = pg.sprite.RenderPlain()
        # A sprite group that contains all close block sprites (render only).
        self.block_render_sprites = pg.sprite.RenderPlain()
        # A sprite group that contains all close enemy sprites (render only).
        self.enemy_render_sprites = pg.sprite.RenderPlain()
        # A sprite group that contains all close sprites (collision only).
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
        # A sprite group that contains all player sprites.
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

            # Fill the screen with the default background color.
            self.screen.fill(GRAY_LIGHT2)

            #
            # Refactor the render sprites group
            #

            # Remove all sprites of the previous loop.
            self.block_render_sprites.empty()
            self.room_render_sprites.empty()
            # Find the new sprites.
            self.block_render_sprites.add(pg.sprite.spritecollide(
                self.screen_sprite, self.block_sprites, False,
                collided=pg.sprite.collide_rect))
            self.room_render_sprites.add(pg.sprite.spritecollide(
                self.screen_sprite, self.room_sprites, False,
                collided=pg.sprite.collide_rect))

            #
            # Updating
            #

            self.player_sprites.update(dt, [direction_x, direction_y])
            # Update all objects here otherwise the mechanism for
            # detecting which objects are on the screen is overridden.
            self.enemy_sprites.update(dt, self.get_offset())
            self.room_sprites.update(self.get_offset())
            self.block_sprites.update(self.get_offset())

            #
            # Drawing
            #

            self.room_render_sprites.draw(self.screen)

            # Currently, all vertices within a virtual screen of
            # 3x width and 3x height of the screen are used. Later
            # when the visibility is limited, this can be further reduced.
            # self.screen_shadow.fill(BLACK)
            # self.player.light.draw(self.screen_shadow)
            # self.screen.blit(self.screen_shadow, (0, 0))

            self.block_render_sprites.draw(self.screen)
            if self.player.bullet:
                self.player.bullet.draw(self.screen, self.get_offset())
            self.player_sprites.draw(self.screen)
            # @todo: Do not draw all enemies later.
            self.enemy_sprites.draw(self.screen)

            # Draw a cross as mouse cursor.
            pg.draw.line(self.screen, BLUE,
                         (self.player.get_aim_x() - 5,
                          self.player.get_aim_y() - 5),
                         (self.player.get_aim_x() + 5,
                          self.player.get_aim_y() + 5))
            pg.draw.line(self.screen, BLUE,
                         (self.player.get_aim_x() - 5,
                          self.player.get_aim_y() + 5),
                         (self.player.get_aim_x() + 5,
                          self.player.get_aim_y() - 5))

            # Debugging
            # Draw navmesh
            # for tri in self.navmesh.mesh:
            #     triangle = [(p[0] - self.game_x, p[1] - self.game_y)
            #                 for p in tri.triangle]
            #     pg.draw.polygon(self.screen, (255, 0, 0), triangle, 1)
            #     for node in tri.nodes:
            #         pg.draw.circle(self.screen, (0, 255, 0),
            #                        (node.position[0] - self.game_x,
            #                         node.position[1] - self.game_y), 2)

            # path = self.enemy_sprites.sprites()[0].path
            # if path:
            #     path = [(p[0] - self.game_x, p[1] - self.game_y) for p in path]
            #     pg.draw.lines(self.screen, (0, 0, 255), False, path)

            self.screen.blit(self.update_fps(), (5, 5))

            # Go ahead and update the screen with what we've drawn.
            # This MUST happen after all the other drawing commands.
            pg.display.flip()
            # This limits the while loop to a max of FPS times per second.
            self.clock.tick(FPS)

    def create_rooms(self, numbers=2):
        rooms = []

        def get_random_even(r1, r2):
            num = 0
            while True:
                num = random.randint(r1, r2)
                if num % 2 == 0:
                    return num

        def get_room_door(options=('top', 'right', 'bottom', 'left')):
            return options[random.randint(0, len(options) - 1)]

        def get_room_size(w_range=(300, 1000), h_range=(300, 1000)):
            return (get_random_even(w_range[0], w_range[1]),
                    get_random_even(h_range[0], h_range[1]))

        def get_oppsite_door(door):
            if 'top' in door:
                return ['bottom']
            elif 'bottom' in door:
                return ['top']
            elif 'left' in door:
                return ['right']
            elif 'right' in door:
                return ['left']

        def get_room_attributes(x_prev, y_prev, w_prev, h_prev, door_prev):
            w, h = get_room_size()
            # Handle position if room is on the top or bottom
            # of the previous room.
            if 'top' in door_prev or 'bottom' in door_prev:
                if 'top' in door_prev:
                    y = y_prev - h
                elif 'bottom' in door_prev:
                    y = y_prev + h_prev
                if w > w_prev:
                    x = x_prev - (w - w_prev)//2
                else:
                    x = x_prev + (w_prev - w)//2
            # Handle position if room is on the left or right
            # of the previous room.
            elif 'left' in door_prev or 'right' in door_prev:
                if 'left' in door_prev:
                    x = x_prev - w
                elif 'right' in door_prev:
                    x = x_prev + w_prev
                if h > h_prev:
                    y = y_prev - (h - h_prev)//2
                else:
                    y = y_prev + (h_prev - h)//2

            # Create doors.
            doors = get_oppsite_door(door_prev)

            return x, y, w, h, doors

        door = get_room_door()
        x = y = 0
        w, h = get_room_size(w_range=(300, 400), h_range=(300, 400))
        # Append the initial room.
        # The initial room doesn't count for the numbers of rooms.
        # So if numbers=0 there is one room (initial room).
        rooms.append(Room(x, y, w, h, self.get_offset(), [door]))

        for i in range(numbers):
            # Saves the attributes of the previous room.
            x_prev = x
            y_prev = y
            w_prev = w
            h_prev = h
            door_prev = door

            # Create temporary room object to check fpr collision.
            collision = True
            attempts = 0
            while collision and attempts < 10:
                collision = False
                x, y, w, h, doors = get_room_attributes(
                    x_prev, y_prev, w_prev, h_prev, door_prev)
                room = Room(x, y, w, h, self.get_offset(), doors)
                for r in rooms:
                    if pg.sprite.collide_rect(r, room):
                        collision = True
                        attempts += 1
                        print("Collide! Create new room.")
                        break

            if not collision:
                # If this is not the last room.
                if i < (numbers - 1):
                    # Only add the new door position if its no exists already.
                    while len(doors) <= 1:
                        door = get_room_door()
                        if door not in doors:
                            doors.append(door)
                # Append room to list.
                rooms.append(Room(x, y, w, h, self.get_offset(), doors))
            else:
                # Break here if the generation of rooms failed.
                break

        return rooms

    def get_player_pos(self):
        return (self.player.get_x(), self.player.get_y())

    def set_offset(self, dx, dy):
        self.game_x = round(self.game_x - dx)
        self.game_y = round(self.game_y - dy)

    def get_offset(self):
        return (self.game_x, self.game_y)

    def get_block_points_on_screen(self):
        _block_points = []
        _offset = self.get_offset()
        _oversized_screen = pg.Rect(
            _offset[0] - SCREEN_RECT.width,
            _offset[1] - SCREEN_RECT.height,
            SCREEN_RECT.width*3,
            SCREEN_RECT.height*3)
        for point in self.unique_block_points:
            if _oversized_screen.collidepoint(point):
                _block_points.append(point)

        return _block_points

    def update_fps(self):
        fps = str(int(self.clock.get_fps()))
        fps_text = self.fps_font.render(fps, 1, RED_LIGHT)
        return fps_text


if __name__ == '__main__':
    game = Game()
    game.start()
