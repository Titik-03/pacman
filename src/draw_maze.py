import arcade
from mazegenerator import MazeGenerator

NORTH = 1  
SOUTH = 2  
EAST = 4   
WEST = 8  


class GameWindow(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Pac-Man")

        self.m = MazeGenerator()
        self.maze = self.m.maze

        self.rows = len(self.maze)
        self.cols = len(self.maze[0])

        self.cell_size = min(width // self.cols,
                             height // self.rows)

        self.sheet = arcade.load_spritesheet(
            "/home/titik/Documents/Study/git/Pac-man/src/assets/walls/walls.png"
        )

        self.wall_textures = self.sheet.get_texture_grid(
            size=(64, 64),
            columns=4,
            count=16,
        )

        self.wall_list = arcade.SpriteList()

        self.build_maze()

    def on_draw(self):
        self.clear()
        self.wall_list.draw()

    def build_maze(self):
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.maze[row][col]

                texture = self.wall_textures[cell]

                sprite = arcade.Sprite(
                    path_or_texture=texture,
                    center_x=col * self.cell_size + self.cell_size / 2,
                    center_y=row * self.cell_size + self.cell_size / 2,
                    scale=self.cell_size / 64,
                )

                self.wall_list.append(sprite)
window = GameWindow(900, 900)
arcade.run()