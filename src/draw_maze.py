import arcade
from mazegenerator import MazeGenerator

# MazeGenerator convention
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

        self.m = MazeGenerator((20, 20))
        self.maze = self.m.maze

        self.rows = len(self.maze)
        self.cols = len(self.maze[0])

        self.cell_size = min(width // self.cols,
                             height // self.rows)

    def on_draw(self):
        self.clear()
        cs = self.cell_size
        
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.maze[row][col]
                x = col * cs
                y = (self.rows - 1 - row) * cs

                if cell & NORTH:
                    arcade.draw_line(x, y + cs, x + cs, y + cs, GLOW, 6)
                    arcade.draw_line(x, y + cs, x + cs, y + cs, NEON, 2)
                if cell & SOUTH:
                    arcade.draw_line(x, y, x + cs, y, GLOW, 6)
                    arcade.draw_line(x, y, x + cs, y, NEON, 2)
                if cell & EAST:
                    arcade.draw_line(x + cs, y, x + cs, y + cs, GLOW, 6)
                    arcade.draw_line(x + cs, y, x + cs, y + cs, NEON, 2)
                if cell & WEST:
                    arcade.draw_line(x, y, x, y + cs, GLOW, 6)
                    arcade.draw_line(x, y, x, y + cs, NEON, 2)


window = GameWindow(900, 900)
arcade.run()