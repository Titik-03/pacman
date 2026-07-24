import arcade
from mazegenerator import MazeGenerator

class GameWindow(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Pac-Man")
        self.m = MazeGenerator()
        self.maze = self.m.maze
        self.rows = len(self.maze)
        self.cols = len(self.maze[0])
    def draw_maze(self):
        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.maze[i][j]
                
