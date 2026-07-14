import arcade

# Bitmask directions
NORTH_MASK = 1
EAST_MASK  = 2
SOUTH_MASK = 4
WEST_MASK  = 8

class PacmanMazeGame(arcade.Window):
    def __init__(self, maze_grid):
        self.maze_grid = maze_grid
        self.rows = len(maze_grid)
        self.cols = len(maze_grid[0]) if self.rows > 0 else 0
        
        # Sizing variables
        self.cell_size = 50
        self.wall_thickness = 4
        
        # Calculate screen size dynamically
        screen_width = self.cols * self.cell_size
        screen_height = self.rows * self.cell_size
        super().__init__(screen_width, screen_height, "A-Maze-ing Pac-man")
        
        # Game State
        self.score = 0
        self.pacman_row = 0  # Spawn at top-left cell
        self.pacman_col = 0
        
        # Generate pellets in all cells
        self.pellets = set()
        for r in range(self.rows):
            for c in range(self.cols):
                self.pellets.add((c, r))
                
        # Eat the first pellet where Pac-man spawns
        self.pellets.discard((self.pacman_col, self.pacman_row))

    def on_draw(self):
        self.clear()
        
        # 1. DRAW THE MAZE WALLS
        for r in range(self.rows):
            for c in range(self.cols):
                val = self.maze_grid[r][c]
                
                # Convert 2D array coordinates (0 at top) to arcade coords (0 at bottom)
                y_idx = self.rows - 1 - r
                
                # Calculate pixel borders for this cell
                x_left = c * self.cell_size
                x_right = (c + 1) * self.cell_size
                y_bottom = y_idx * self.cell_size
                y_top = (y_idx + 1) * self.cell_size
                
                # Bit 0: North
                if val & NORTH_MASK:
                    arcade.draw_line(x_left, y_top, x_right, y_top, arcade.color.BLUE, self.wall_thickness)
                # Bit 1: East
                if val & EAST_MASK:
                    arcade.draw_line(x_right, y_bottom, x_right, y_top, arcade.color.BLUE, self.wall_thickness)
                # Bit 2: South
                if val & SOUTH_MASK:
                    arcade.draw_line(x_left, y_bottom, x_right, y_bottom, arcade.color.BLUE, self.wall_thickness)
                # Bit 3: West
                if val & WEST_MASK:
                    arcade.draw_line(x_left, y_bottom, x_left, y_top, arcade.color.BLUE, self.wall_thickness)
        # 2. DRAW THE PELLETS
        for pellet in list(self.pellets):
            p_col, p_row = pellet
            p_y_idx = self.rows - 1 - p_row
            px = (p_col + 0.5) * self.cell_size
            py = (p_y_idx + 0.5) * self.cell_size
            arcade.draw_circle_filled(px, py, 4, arcade.color.ORANGE)

        # 3. DRAW PACMAN
        pac_y_idx = self.rows - 1 - self.pacman_row
        pac_x = (self.pacman_col + 0.5) * self.cell_size
        pac_y = (pac_y_idx + 0.5) * self.cell_size
        arcade.draw_circle_filled(pac_x, pac_y, 14, arcade.color.YELLOW)

        # 4. DRAW SCOREBOARD
        arcade.draw_text(
            f"Score: {self.score}", 
            10, self.height - 25, 
            arcade.color.WHITE, 12, bold=True
        )

    def on_key_press(self, key, modifiers):
        # Retrieve the wall layout of Pacman's current cell
        current_cell_walls = self.maze_grid[self.pacman_row][self.pacman_col]
        
        # UP ARROW -> Move North (if North wall is open & not at top border)
        if key == arcade.key.UP:
            if (current_cell_walls & NORTH_MASK) == 0 and self.pacman_row > 0:
                self.pacman_row -= 1
                
        # DOWN ARROW -> Move South (if South wall is open & not at bottom border)
        elif key == arcade.key.DOWN:
            if (current_cell_walls & SOUTH_MASK) == 0 and self.pacman_row < self.rows - 1:
                self.pacman_row += 1
                
        # LEFT ARROW -> Move West (if West wall is open & not at left border)
        elif key == arcade.key.LEFT:
            if (current_cell_walls & WEST_MASK) == 0 and self.pacman_col > 0:
                self.pacman_col -= 1
                
        # RIGHT ARROW -> Move East (if East wall is open & not at right border)
        elif key == arcade.key.RIGHT:
            if (current_cell_walls & EAST_MASK) == 0 and self.pacman_col < self.cols - 1:
                self.pacman_col += 1

        # Check if Pac-man ate a pellet in the new cell
        current_pos = (self.pacman_col, self.pacman_row)
        if current_pos in self.pellets:
            self.pellets.remove(current_pos)
            self.score += 10


# This matches the user's sample output representation
# Let's mock a solvable sample generated grid
# Bits: N=1, E=2, S=4, W=8
sample_generated_map = [
    [12, 5,  5,  3], # Row 0 (Top)
    [12, 5,  1,  3], # Row 1
    [12, 5,  4,  3], # Row 2
    [12, 5,  5,  3], # Row 3
    [12, 5,  5,  6]  # Row 4 (Bottom)
]

def main():
    game = PacmanMazeGame(sample_generated_map)
    arcade.run()

if __name__ == "__main__":
    main()