import math
import pathlib
import arcade
import arcade.shape_list as shapes
from mazegenerator import MazeGenerator
from src.coins import Coin
from src.player import Player
from src.pause_menu import PauseMenu
from src.game_over import GameOver
from src.vectory import Vectory
from src.ghost import Blinky, Pinky, Inky, Clyde


SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
BLINKY_PATH = SCRIPT_DIR / "assets" / "blinky.png"
PINKY_PATH = SCRIPT_DIR / "assets" / "pinky.png"
# INKY_PATH = SCRIPT_DIR / "assets" / "ghost.png"
# CLYDE_PATH = SCRIPT_DIR / "assets" / "ghost.png"

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

NEON = (0, 255, 255)
GLOW = (0, 100, 200, 100)


class GameWindow(arcade.View):

    def __init__(self,
                 menu: arcade.View,
                 window: arcade.Window,
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

        margin = 40
        available_w = self.width - margin * 2
        available_h = self.height - margin * 2
        self.cell_size = min(available_w // self.cols, available_h // self.rows)

        self.offset_x = (self.width - self.cols * self.cell_size) / 2
        self.offset_y = (self.height - self.rows * self.cell_size) / 2

        self.coin = Coin(10, 10)
        self.score = 0


        #player coords.
        center_col = self.cols // 2
        center_row = self.rows // 2
        start_x = self.offset_x + (center_col + 0.5) * self.cell_size
        start_y = self.offset_y + (self.rows - 1 - center_row + 0.5) * self.cell_size

        self.player, self.player_list = Player.create_player(start_x, start_y, self.cell_size)


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
        self.pause_menu = PauseMenu(self)
        self.pause = False
        self.timer = 60

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


    def on_draw(self):
        self.clear()
        self.wall_shapes.draw()
        self.player_list.draw()
        self.blinky_list.draw()
        self.pinky_list.draw()
        self.inky_list.draw()
        self.clyde_list.draw()

        for i in self.coins_lst:
            i.draw()

        if self.pause:
            self.manager.draw()

        arcade.draw_text(f"{int(self.timer)}", 1500, 1000)


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
        )

        self.clyde.chase_player(
            self.player,
            self.maze,
            self.cell_size,
            self.rows,
            self.cols,
            self.offset_x,
            self.offset_y,
            delta_time,
        )


    def on_update(self, delta_time: float):

        if self.pause:
            return

        self.timer -= delta_time
        if self.timer < 0.80:
            self.window.show_view(self.game_over)

        self.player.update_grid_movement(
            self.maze,
            self.cell_size,
            self.rows,
            self.cols,
            self.offset_x,
            self.offset_y,
            delta_time,
        )


        self.ghosts_chase_player(delta_time)


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
            self.window.show_view(self.vectory)

    def on_key_release(self, key, modifiers):
        self.player.on_key_release(key)


    def on_show_view(self):

        self.manager.enable()

        menu_elements = arcade.gui.UIBoxLayout(space_between=40)

        #button style.
        button_style = {
            "normal": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name=("georgia", "times new roman", "serif"),
                font_color=(234, 236, 250),
                bg=(20, 12, 48),
                border=(90, 72, 160),
                border_width=2,
            ),
            "hover": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name=("georgia", "times new roman", "serif"),
                font_color=(250, 250, 255),
                bg=(64, 32, 120),
                border=(180, 170, 255),
                border_width=2,
            ),
            "press": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name=("georgia", "times new roman", "serif"),
                font_color=(252, 244, 255),
                bg=(8, 6, 26),
                border=(110, 78, 190),
                border_width=3,
            ),
            "disabled": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name=("georgia", "times new roman", "serif"),
                font_color=(120, 118, 136),
                bg=(18, 18, 36),
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
            self.pause = not self.pause
            return

        if self.pause:
            return

        self.player.on_key_press(key)

        if key == arcade.key.F1:     #this is just for testing. Has to be changed!!!!
            self.game_over = GameOver(self.window, self.main_menu, self.score)
            self.window.show_view(self.game_over)

        if key == arcade.key.F2:
            self.vectory = Vectory(self.window, self.main_menu, self.score)
            self.window.show_view(self.vectory)

