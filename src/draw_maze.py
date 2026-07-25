import arcade
import arcade.shape_list as shapes
from mazegenerator import MazeGenerator
from player import Player

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

NEON = (0, 255, 255)
GLOW = (0, 100, 200, 100)


class GameWindow(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Pac-Man")
        arcade.set_background_color((10, 10, 30))

        self.m = MazeGenerator((10, 10))
        self.maze = self.m.maze

        self.rows = len(self.maze)
        self.cols = len(self.maze[0])

        self.cell_size = min(width // self.cols,
                             height // self.rows)

        start_x = self.cell_size / 2
        start_y = (self.rows - 1) * self.cell_size + self.cell_size / 2
        self.player, self.player_list = Player.create_player(start_x, start_y, self.cell_size)

        self.wall_shapes = shapes.ShapeElementList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        cs = self.cell_size
        wall_thickness = 4

        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.maze[row][col]
                x = col * cs
                y = (self.rows - 1 - row) * cs

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

    def on_update(self, delta_time: float):
        self.player.update_grid_movement(self.maze, self.cell_size, self.rows, self.cols)




    def on_key_press(self, key, modifiers):
        self.player.on_key_press(key)

    def on_key_release(self, key, modifiers):
        self.player.on_key_release(key)


if __name__ == "__main__":
    window = GameWindow(900, 900)
    arcade.run()