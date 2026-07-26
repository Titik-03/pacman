import math
import arcade
import arcade.shape_list as shapes
from mazegenerator import MazeGenerator
from coins import Coin
from player import Player

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

NEON = (0, 255, 255)
GLOW = (0, 100, 200, 100)


class GameWindow(arcade.Window):
    def __init__(self, width=None, height=None, fullscreen=True):
        if fullscreen:
            super().__init__(title="Pac-Man", resizable=True, fullscreen=True)
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

        center_col = self.cols // 2
        center_row = self.rows // 2
        start_x = self.offset_x + (center_col + 0.5) * self.cell_size
        start_y = self.offset_y + (self.rows - 1 - center_row + 0.5) * self.cell_size
        self.player, self.player_list = Player.create_player(start_x, start_y, self.cell_size)

        self.wall_shapes = shapes.ShapeElementList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coins_lst = []
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

        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.wall_list)

    def on_draw(self):
        self.clear()
        self.wall_shapes.draw()
        self.player_list.draw()
        for i in self.coins_lst:
            i.draw()

    def on_update(self, delta_time: float):
        self.player.update_grid_movement(self.maze, self.cell_size, self.rows, self.cols, self.offset_x, self.offset_y)

        for coin in self.coins_lst:
            if not coin.is_eaten:
                distance = math.hypot(self.player.center_x - coin.x, self.player.center_y - coin.y)
                if distance < (self.player.width / 2 + coin.radius):
                    coin.is_eaten = True
                    self.score += 50 if coin.is_powerup else 1

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.close()
        self.player.on_key_press(key)

    def on_key_release(self, key, modifiers):
        self.player.on_key_release(key)


if __name__ == "__main__":
    window = GameWindow(fullscreen=True)
    arcade.run()