import arcade
from mazegenerator import MazeGenerator


# Define direction bitmask constants
NORTH = 1  # 0001
SOUTH = 2  # 0010
EAST = 4   # 0100
WEST = 8   # 1000

SPRITE_SIZE = 32  # Size of each cell grid tile in pixels


class MazeView(arcade.View):
    """Handles rendering and logic for the Pacman maze gameplay."""

    def __init__(self, maze_grid: list[list[int]]) -> None:
        """Initialize the game view with the 2D maze grid bitmask data."""
        super().__init__()
        self.maze_grid = maze_grid
        
        # Calculate grid dimensions
        self.grid_height = len(maze_grid)
        self.grid_width = len(maze_grid[0]) if self.grid_height > 0 else 0

        # Sprite lists for optimized rendering performance
        self.wall_list: arcade.SpriteList = arcade.SpriteList()
        self.pacgum_list: arcade.SpriteList = arcade.SpriteList()

        self.setup_maze()

    def setup_maze(self) -> None:
        """Decode the bitmask grid and populate the sprite lists."""
        for row_idx, row in enumerate(self.maze_grid):
            for col_idx, bitmask in enumerate(row):
                # Calculate screen coordinates based on center of the tile
                # Arcade (0,0) is bottom-left, grids are often top-down. 
                # Reversing row coordinates handles inversion nicely if needed.
                x = col_idx * SPRITE_SIZE + (SPRITE_SIZE / 2)
                y = (self.grid_height - 1 - row_idx) * SPRITE_SIZE + (SPRITE_SIZE / 2)

                # 1. Draw outer boundaries or explicit wall tiles if mask specifies
                # 2. Alternatively, parse individual wall segments per cell:
                if bitmask & NORTH:
                    self._create_wall_segment(x, y + SPRITE_SIZE / 2, SPRITE_SIZE, 4)
                if bitmask & SOUTH:
                    self._create_wall_segment(x, y - SPRITE_SIZE / 2, SPRITE_SIZE, 4)
                if bitmask & EAST:
                    self._create_wall_segment(x + SPRITE_SIZE / 2, y, 4, SPRITE_SIZE)
                if bitmask & WEST:
                    self._create_wall_segment(x - SPRITE_SIZE / 2, y, 4, SPRITE_SIZE)

                # Populate pacgums in open areas (e.g., if it's a valid corridor)
                # Ensure you avoid placing them directly on the player spawn point!
                if bitmask != 15:  # Not completely enclosed wall block
                    pacgum = arcade.SpriteCircle(radius=4, color=arcade.color.WHITE)
                    pacgum.position = (x, y)
                    self.pacgum_list.append(pacgum)

    def _create_wall_segment(self, x: float, y: float, width: int, height: int) -> None:
        """Helper to create and place a solid color rectangle sprite as a wall."""
        wall = arcade.SpriteSolidColor(width=width, height=height, color=arcade.color.BLUE)
        wall.position = (x, y)
        self.wall_list.append(wall)

    def on_show_view(self) -> None:
        """Set up background colors when switching to this view."""
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear()
        
        # Draw everything efficiently via SpriteLists
        self.wall_list.draw()
        # self.pacgum_list.draw()

def main() -> None:
    """Main entry point for running the game engine."""
    # Dummy mock example of an external 4x4 bitmask grid layout
    m = MazeGenerator()
    sample_maze = m.maze

    # Dynamically scale window bounds based on grid size
    screen_width = len(sample_maze[0]) * SPRITE_SIZE
    screen_height = len(sample_maze) * SPRITE_SIZE

    window = arcade.Window(screen_width, screen_height, "Pacman: The Shattered Legacy", resizable=True)
    game_view = MazeView(sample_maze)
    window.show_view(game_view)
    arcade.run()

if __name__ == "__main__":
    main()