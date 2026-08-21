from arcade import load_texture
import random
import math
import pathlib
import arcade
import arcade.shape_list as shapes
from mazegenerator import MazeGenerator
from src.coins import Coin
from src.player import Player
# from src.pause_menu import PauseMenu
from src.game_over import GameOver
from src.vectory import Vectory
from src.ghost import Blinky, Pinky, Inky, Clyde
from src.cheat_menu import CheatMenu
from src.particle import ShatterParticle


SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
BLINKY_PATH = SCRIPT_DIR / "assets" / "blinky.png"
PINKY_PATH = SCRIPT_DIR / "assets" / "pinky.png"
# INKY_PATH = SCRIPT_DIR / "assets" / "ghost.png"
# CLYDE_PATH = SCRIPT_DIR / "assets" / "ghost.png"

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

# Catppuccin Mocha Palette
MOCHA_BASE = (30, 30, 46)        # #1e1e2e
MOCHA_TEXT = (205, 214, 244)     # #cdd6f4
MOCHA_MAUVE = (203, 166, 247)    # #cba6f7
MOCHA_LAVENDER = (180, 190, 254) # #b4befe
MOCHA_CRUST = (17, 17, 27)       # #11111b
MOCHA_RED = (243, 139, 168)      # #f38ba8
MOCHA_SURFACE0 = (49, 50, 68)    # #313244
MOCHA_SURFACE1 = (69, 71, 90)    # #45475a
MOCHA_MANTLE = (24, 24, 37)      # #181825

NEON = MOCHA_MAUVE
GLOW = (203, 166, 247, 80)



class GameWindow(arcade.View):

    def __init__(self,
                 menu: arcade.View,
                 window: arcade.Window,
                 seed: int,
                 width=None,
                 height=None,
                 fullscreen=True
                 ) -> None:

        if fullscreen:
            super().__init__()
        else:
            super().__init__(width or 900, height or 900, "Pac-Man", resizable=True)
        arcade.set_background_color((10, 10, 30))

        self.m = MazeGenerator()
        self.maze = self.m.maze

        self.rows = len(self.maze)
        self.cols = len(self.maze[0])
        self.background = load_texture("src/assets/Dek.png")

        # Position maze within the dark left area of Dek.png
        left_area_width = self.width * 0.52
        margin_x = 80
        margin_y = 100
        available_w = left_area_width - margin_x
        available_h = self.height - margin_y
        self.cell_size = min(available_w // self.cols, available_h // self.rows)

        self.offset_x = (left_area_width - self.cols * self.cell_size) / 2
        self.offset_y = (self.height - self.rows * self.cell_size) / 2

        self.coin = Coin(10, 10)
        self.score = 0
        self.level = 1

        # Load Handjet font
        font_path = SCRIPT_DIR / "assets" / "Handjet" / "static" / "Handjet-Bold.ttf"
        if font_path.exists():
            arcade.load_font(str(font_path))

        # Text UI objects positioned next to labels in Dek.png
        font_sz = int(32 * (self.height / 1080.0))
        self.score_text = arcade.Text(
            text=f"{self.score}",
            x=self.width * 0.77,
            y=self.height * 0.97,
            color=MOCHA_CRUST,
            font_size=font_sz,
            font_name="Handjet",
            bold=True,
            anchor_y="center"
        )

        self.lives_x = self.width * 0.81
        self.lives_y = self.height * 0.875

        self.level_text = arcade.Text(

            text=f"{self.level}",
            x=self.width * 0.84,
            y=self.height * 0.784,
            color=MOCHA_CRUST,
            font_size=font_sz,
            font_name="Handjet",
            bold=True,
            anchor_y="center"
        )

        self.time_text = arcade.Text(
            text=f"{int(120)}s",
            x=self.width * 0.87,
            y=self.height * 0.698,
            color=MOCHA_CRUST,
            font_size=font_sz,
            font_name="Handjet",
            bold=True,
            anchor_y="center"
        )

        #player coords.
        center_col = self.cols // 2
        center_row = self.rows // 2
        start_x = self.offset_x + (center_col + 0.5) * self.cell_size
        start_y = self.offset_y + (self.rows - 1 - center_row + 0.5) * self.cell_size

        self.player, self.player_list = Player.create_player(start_x, start_y, self.cell_size)
        self.player_spawn_x = start_x
        self.player_spawn_y = start_y

        self.player_speed = self.player.speed
        self.speed_up = False

        self.init_ghosts()

        self.wall_shapes = shapes.ShapeElementList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coins_lst = []

        self.init_maze()

        self.target_score = len(self.coins_lst) + 196

        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.wall_list)

        self.manager = arcade.gui.UIManager()
        
        self.main_menu = menu
        self.window = window
        # self.pause_menu = PauseMenu(self)
        self.cheat_menu = CheatMenu(self)
        self.pause = False
        self.timer = 120
        self.cheat_menu = False
        self.cheat_menu_timer = 0.0

        self.debug = False
        self.freeze_ghosts = False

        self.game_over = GameOver(self.window, self.main_menu, self.score)
        self.vectory = Vectory(self.window, self.main_menu, self.score)
        self.shatter_particles: list[ShatterParticle] = []


    def init_ghosts(self):

        #Blinky init.
        blinky_row = 0
        blinky_col = 0

        blinky_x = self.offset_x + (blinky_col + 0.5) * self.cell_size
        blinky_y = self.offset_y + (self.rows - 1 - blinky_row + 0.5) * self.cell_size

        self.blinky, self.blinky_list = Blinky.create_ghost(
            blinky_x,
            blinky_y,
            self.cell_size,
            "blinky"
        )

        self.blinky.home_row, self.blinky.home_col = self.blinky.get_cell(
            self.blinky.center_x,
            self.blinky.center_y,
            self.cell_size,
            self.rows,
            self.offset_x,
            self.offset_y
        )

        #Pinky init.
        pinky_row = 0
        pinky_col = self.cols - 1

        pinky_x = self.offset_x + (pinky_col + 0.5) * self.cell_size
        pinky_y = self.offset_y + (self.rows - 1 - pinky_row + 0.5) * self.cell_size

        self.pinky, self.pinky_list = Pinky.create_ghost(
            pinky_x,
            pinky_y,
            self.cell_size,
            "pinky"
        )

        self.pinky.home_row, self.pinky.home_col = self.pinky.get_cell(
            self.pinky.center_x,
            self.pinky.center_y,
            self.cell_size,
            self.rows,
            self.offset_x,
            self.offset_y
        )

        #Inky init.
        inky_row = self.rows - 1
        inky_col = 0

        inky_x = self.offset_x + (inky_col + 0.5) * self.cell_size
        inky_y = self.offset_y + (self.rows - 1 - inky_row + 0.5) * self.cell_size

        self.inky, self.inky_list = Inky.create_ghost(
            inky_x,
            inky_y,
            self.cell_size,
            "inky"
        )

        self.inky.home_row, self.inky.home_col = self.inky.get_cell(
            self.inky.center_x,
            self.inky.center_y,
            self.cell_size,
            self.rows,
            self.offset_x,
            self.offset_y
        )


        #Clyde init.
        clyde_row = self.rows - 1
        clyde_col = self.cols - 1

        clyde_x = self.offset_x + (clyde_col + 0.5) * self.cell_size
        clyde_y = self.offset_y + (self.rows - 1 - clyde_row + 0.5) * self.cell_size

        self.clyde, self.clyde_list = Clyde.create_ghost(
            clyde_x,
            clyde_y,
            self.cell_size,
            "clyde"
        )

        self.clyde.home_row, self.clyde.home_col = self.clyde.get_cell(
            self.clyde.center_x,
            self.clyde.center_y,
            self.cell_size,
            self.rows,
            self.offset_x,
            self.offset_y
        )


    def init_maze(self):

        cs = self.cell_size
        wall_thickness = 4

        corner_cells = {
            (0, 0),
            (0, self.cols - 1),
            (self.rows - 1, 0),
            (self.rows - 1, self.cols - 1)
        }

        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.maze[row][col]
                x = self.offset_x + col * cs
                y = self.offset_y + (self.rows - 1 - row) * cs
                if (row, col) in corner_cells:
                    self.coins_lst.append(Coin(x + cs / 2, y + cs / 2, is_powerup=True))
                elif cell & 0b1111 != 0b1111:
                    self.coins_lst.append(Coin(x + cs / 2, y + cs / 2, is_powerup=False))
                elif cell & 0b1111 == 0b1111:
                    self.wall_shapes.append(shapes.create_rectangle(x + cs / 2, y + cs / 2, cs - 3, cs - 3, MOCHA_RED))
                if cell & NORTH:
                    self.wall_shapes.append(shapes.create_line(x, y + cs, x + cs, y + cs, GLOW, 6))
                    self.wall_shapes.append(shapes.create_line(x, y + cs, x + cs, y + cs, NEON, 2))
                    w = arcade.SpriteSolidColor(int(cs), wall_thickness, color=(0, 0, 0, 0))
                    w.center_x = x + cs / 2
                    w.center_y = y + cs
                    self.wall_list.append(w)

                if cell & SOUTH:
                    self.wall_shapes.append(shapes.create_line(x, y, x + cs, y, GLOW, 6))
                    self.wall_shapes.append(shapes.create_line(x, y, x + cs, y, NEON, 2))
                    w = arcade.SpriteSolidColor(int(cs), wall_thickness, color=(0, 0, 0, 0))
                    w.center_x = x + cs / 2
                    w.center_y = y
                    self.wall_list.append(w)

                if cell & EAST:
                    self.wall_shapes.append(shapes.create_line(x + cs, y, x + cs, y + cs, GLOW, 6))
                    self.wall_shapes.append(shapes.create_line(x + cs, y, x + cs, y + cs, NEON, 2))
                    w = arcade.SpriteSolidColor(wall_thickness, int(cs), color=(0, 0, 0, 0))
                    w.center_x = x + cs
                    w.center_y = y + cs / 2
                    self.wall_list.append(w)

                if cell & WEST:
                    self.wall_shapes.append(shapes.create_line(x, y, x, y + cs, GLOW, 6))
                    self.wall_shapes.append(shapes.create_line(x, y, x, y + cs, NEON, 2))
                    w = arcade.SpriteSolidColor(wall_thickness, int(cs), color=(0, 0, 0, 0))
                    w.center_x = x
                    w.center_y = y + cs / 2
                    self.wall_list.append(w)


    def draw_background_image(self):
        self.clear()
        arcade.draw_texture_rect(
        self.background,
        arcade.LBWH(
            0,
            0,
            self.width,
            self.height
        )
    )


    def draw_maze_background(self):
        maze_width = self.cols * self.cell_size
        maze_height = self.rows * self.cell_size
        
        arcade.draw_rect_filled(
            arcade.LBWH(
                self.offset_x,       # Left edge of the maze
                self.offset_y,       # Bottom edge of the maze
                maze_width,          # Total maze width
                maze_height          # Total maze height
            ),
            color=(30, 30, 46, 220))
        arcade.draw_rect_outline(
            arcade.LBWH(
                self.offset_x,
                self.offset_y,
                maze_width + 1,
                maze_height + 1
            ),
            color=MOCHA_MAUVE,  # Mauve neon border
            border_width=2
        )


    def draw_debug(self):

        self.blinky.draw_target_x(self.cell_size, self.offset_x, self.offset_y, rows=self.rows, color=arcade.color.RED)
        self.pinky.draw_target_x(self.cell_size, self.offset_x, self.offset_y, rows=self.rows, color=arcade.color.PINK)
        self.inky.draw_target_x(self.cell_size, self.offset_x, self.offset_y, rows=self.rows, color=arcade.color.CYAN)
        self.clyde.draw_target_x(self.cell_size, self.offset_x, self.offset_y, rows=self.rows, color=arcade.color.ORANGE)

    def draw_hearts(self):
        # Draw red hearts for lives next to LIVES: label in Dek.png
        size = 14 * (self.height / 1080.0)
        spacing = 38 * (self.width / 1920.0)
        color = MOCHA_RED


        for i in range(max(0, self.player.lives)):
            cx = self.lives_x + i * spacing
            cy = self.lives_y
            arcade.draw_circle_filled(cx - size * 0.35, cy + size * 0.15, size * 0.4, color)
            arcade.draw_circle_filled(cx + size * 0.35, cy + size * 0.15, size * 0.4, color)
            arcade.draw_triangle_filled(
                cx - size * 0.72, cy + size * 0.15,
                cx + size * 0.72, cy + size * 0.15,
                cx, cy - size * 0.7,
                color
            )

    def draw_cheat_menu(self):
        #blur.
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                self.width / 2, 
                self.height / 2, 
                self.width, 
                self.height
            ),
            color=(10, 10, 20, 200)
        )

        menu_w, menu_h = 550, 670
        cx, cy = self.width / 2, self.height / 2

        arcade.draw_rect_filled(
            arcade.rect.XYWH(cx, cy, menu_w, menu_h),
            color=(25, 25, 35, 240)
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(cx, cy, menu_w, menu_h),
            color=MOCHA_LAVENDER,
            border_width=3
        )

        arcade.draw_text(
            "CHEAT MENU",
            x=cx,
            y=cy + 290,
            color=MOCHA_MAUVE,
            font_size=55,
            anchor_x="center",
            anchor_y="center",
            font_name="Handjet",
            bold=True
        )

        cheats = [
            "[F1 / ESC] TO Close Menu",
            f"[F2] Toggle Invincibility: {'ON' if self.player.invincible else 'OFF'}",
            f"[F3] Trigger Power Pellet: {'ON' if self.player.is_powered_up else 'OFF'}",
            f"[F4] Toggle Freeze all ghosts: {'ON' if self.freeze_ghosts else 'OFF'}",
            f"[F5] Toggle paths Debug: {'ON' if self.debug else 'OFF'}",
            f"[F6] Toggle Speed: {'ON' if self.speed_up else 'OFF'}",
            "[F7] Add +1 Life",
            "[F8] Skip the level",
        ]

        start_y = cy + 200
        for i, line in enumerate(cheats):
            arcade.draw_text(
                line,
                x=cx,
                y=start_y - (i * 70),
                #(i * 40) is how far from each other.
                color=arcade.color.WHITE,
                font_size=25,
                anchor_x="center",
                anchor_y="center",
                font_name="Handjet",
                bold=True
            )


    def on_draw(self):
        self.clear()
        self.draw_background_image()
        self.draw_maze_background()
        self.wall_shapes.draw()

        for i in self.coins_lst:
            i.draw()

        self.player_list.draw()
        self.blinky_list.draw()
        self.pinky_list.draw()
        self.inky_list.draw()
        self.clyde_list.draw()

        for particle in self.shatter_particles:
            particle.draw()


        self.score_text.text = f"{self.score}"
        self.level_text.text = f"{self.level}"
        self.time_text.text = f"{int(self.timer)}s"

        self.score_text.draw()
        self.draw_hearts()
        self.level_text.draw()
        self.time_text.draw()

        if self.debug:
            self.draw_debug()

        if self.cheat_menu:
            self.draw_cheat_menu()

        if self.pause:
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    self.width / 2,
                    self.height / 2,
                    self.width,
                    self.height
                ),
                color=(10, 10, 20, 200)
            )
            self.manager.draw()

    def go_to_game_over(self):
        self.shatter_particles.clear()
        self.player.visible = True
        self.game_over = GameOver(self.window, self.main_menu, self.score)
        self.window.show_view(self.game_over)


    def go_to_vectory(self):
        self.vectory = Vectory(self.window, self.main_menu, self.score)
        self.window.show_view(self.vectory)


    def ghosts_chase_player(self, delta_time):

        self.blinky.chase_player(
            self.player,
            self.maze,
            self.cell_size,
            self.rows,
            self.cols,
            self.offset_x,
            self.offset_y,
            delta_time
        )

        self.pinky.chase_player(
            self.player,
            self.maze,
            self.cell_size,
            self.rows,
            self.cols,
            self.offset_x,
            self.offset_y,
            delta_time
        )

        self.inky.chase_player(
            self.player,
            self.maze,
            self.cell_size,
            self.rows,
            self.cols,
            self.offset_x,
            self.offset_y,
            delta_time,
            blinky=self.blinky
        )

        self.clyde.chase_player(
            self.player,
            self.maze,
            self.cell_size,
            self.rows,
            self.cols,
            self.offset_x,
            self.offset_y,
            delta_time
        )


    def on_update(self, delta_time: float):

        if self.pause or self.cheat_menu:
            return

        if self.shatter_particles:
            self.shatter_particles = [p for p in self.shatter_particles if p.update(delta_time)]
            if not self.shatter_particles:
                if self.player.lives <= 0:
                    self.go_to_game_over()
                else:
                    self.respawn_after_death()
            return

        if self.player.is_dying:
            self.player.update_animation(delta_time)
            if not self.player.is_dying:
                self.player.visible = False
                self.shatter_particles = [
                    ShatterParticle(self.player.center_x, self.player.center_y)
                    for _ in range(16)
                ]
            return

        self.timer -= delta_time
        if self.timer < 0.80:
            self.go_to_game_over()
            return

        self.player.update_grid_movement(
            self.maze,
            self.cell_size,
            self.rows,
            self.cols,
            self.offset_x,
            self.offset_y,
            delta_time,
        )
        self.player.update_animation(delta_time)

        if not self.freeze_ghosts:
            self.ghosts_chase_player(delta_time)
        self.check_ghost_collisions()


        for coin in self.coins_lst:
            if not coin.is_eaten:
                distance = math.hypot(self.player.center_x - coin.x, self.player.center_y - coin.y)
                if distance < (self.player.width / 2 + coin.radius):
                    coin.is_eaten = True
                    if coin.is_powerup:
                        self.score += 50
                        self.player.activate_power_up(10) #power up.
                    else:
                        self.score += 10

        if self.score == self.target_score:
            #change the view to vectory menu.
            self.go_to_vectory()


    def check_ghost_collisions(self):
        """Handles Pac-Man <-> ghost contact: taking damage or eating a scared ghost."""
        if self.player.is_dying or self.shatter_particles:
            return

        for ghost in (self.blinky, self.pinky, self.inky, self.clyde):
            if ghost.state == "EATEN":
                continue

            distance = math.hypot(
                self.player.center_x - ghost.center_x,
                self.player.center_y - ghost.center_y,
            )
            if distance >= (self.player.width / 2 + ghost.width / 2):
                continue

            if ghost.state == "FRIGHTENED":
                self.score += 200
                ghost.get_hit()

            elif (not self.player.invincible) and ghost.can_damage:
                self.handle_player_hit()
                break


    def handle_player_hit(self):
        if self.player.is_dying or self.shatter_particles:
            return
        self.player.take_damage()
        self.player.start_death_animation()


    def respawn_after_death(self):
        # Respawn player at the maze center and send active ghosts back home.
        self.shatter_particles.clear()
        self.player.visible = True
        self.player.respawn_at(self.player_spawn_x, self.player_spawn_y)
        self.player.invincible = True
        self.player.invincible_timer = self.player.INVINCIBILITY_DURATION

        for ghost in (self.blinky, self.pinky, self.inky, self.clyde):
            if ghost.state == "EATEN":
                continue
            x, y = ghost.get_cell_center(
                ghost.home_row, ghost.home_col, self.cell_size, self.rows, self.offset_x, self.offset_y
            )
            ghost.center_x = ghost.target_x = x
            ghost.center_y = ghost.target_y = y
            ghost.state = "CHASE"
            ghost.texture = arcade.load_texture(ghost.normal_texture_path)


    def on_key_release(self, key, modifiers):
        self.player.on_key_release(key)


    def on_show_view(self):

        self.manager.enable()

        menu_elements = arcade.gui.UIBoxLayout(space_between=40)

        #button style.
        button_style = {
            "normal": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name="Handjet",
                font_color=MOCHA_TEXT,
                bg=MOCHA_SURFACE0,
                border=MOCHA_MAUVE,
                border_width=2,
            ),
            "hover": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name="Handjet",
                font_color=MOCHA_TEXT,
                bg=MOCHA_SURFACE1,
                border=MOCHA_LAVENDER,
                border_width=2,
            ),
            "press": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name="Handjet",
                font_color=MOCHA_TEXT,
                bg=MOCHA_MANTLE,
                border=MOCHA_MAUVE,
                border_width=3,
            ),
            "disabled": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name="Handjet",
                font_color=(120, 118, 136),
                bg=MOCHA_CRUST,
                border=(56, 64, 96),
                border_width=1,
            )
        }

        #init the buttons.
        resume_game = arcade.gui.UIFlatButton(text="RESUME GAME", width=300, height=100, style=button_style)
        quit_game = arcade.gui.UIFlatButton(text="MAIN_MENU", width=300, height=100, style=button_style)

        #nested function to do things if the buttons was clicked.
        @resume_game.event("on_click")
        def on_click_start(event):
            #This is the action! Swap from current menu view to game view.
            self.pause = False

        @quit_game.event("on_click")
        def on_click_quit(event):
            self.window.show_view(self.main_menu)
            self.pause = False

        #adding buttons to one group layout.
        menu_elements.add(resume_game)
        menu_elements.add(quit_game)

        #give the group to the manager.
        self.manager.add(
            arcade.gui.UIAnchorLayout(
                anchor_x="center_x",
                anchor_y="center_y",
                children=[menu_elements]
            )
        )


    def on_hide_view(self):
            self.manager.disable()


    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.cheat_menu:
                self.cheat_menu = False
            elif self.pause or not self.pause:
                self.pause = (not self.pause)
            return

        if self.pause or self.player.is_dying or self.shatter_particles:
            return

        self.player.on_key_press(key)

        if key == arcade.key.F1:
            self.cheat_menu = (not self.cheat_menu)

        if key == arcade.key.F2:
            if self.cheat_menu:
                self.player.invincible = (not self.player.invincible)
                self.player.invincible_timer = 9999999999 if self.player.invincible else 0

        if key == arcade.key.F3:
            if self.cheat_menu:
                self.player.is_powered_up = (not self.player.is_powered_up)
                self.player.power_timer = 9999999999 if self.player.is_powered_up else 0

        if key == arcade.key.F4:
            if self.cheat_menu:
                self.freeze_ghosts = (not self.freeze_ghosts)

        if key == arcade.key.F5:
            if self.cheat_menu:
                if self.debug:
                    self.debug = False
                else:
                    self.debug = True

        if key == arcade.key.F6:
            if self.cheat_menu:
                self.speed_up = (not self.speed_up)
                self.player.speed = self.player_speed * 2 if self.speed_up else self.player_speed

        if key == arcade.key.F7:
            if self.cheat_menu:
                self.player.lives += 1

        if key == arcade.key.F8:
            if self.cheat_menu:
                self.main_menu.new_game(random.random())


            

