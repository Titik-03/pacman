from src.player import Player
import math
import random
import pathlib
from collections import deque

import arcade

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
BLINKY_PATH = SCRIPT_DIR / "assets" / "blinky.png"
PINKY_PATH = SCRIPT_DIR / "assets" / "pinky.png"
INKY_PATH = SCRIPT_DIR / "assets" / "inky.png"
CLYDE_PATH = SCRIPT_DIR / "assets" / "clyde.png"
SCARED_PATH = SCRIPT_DIR / "assets" / "scared.png"


class Ghost(arcade.Sprite):
    def __init__(self, center_x: float, center_y: float, texture_path, name: str) -> None:
        super().__init__(path_or_texture=texture_path)
        self.center_x = center_x
        self.center_y = center_y
        self.target_x = center_x
        self.target_y = center_y
        self.speed = 130.0
        self.current_dir = (0, 0)

        # Power-Up System
        self.is_powered_up = False
        self.power_timer = 0.0

        # Ghost state: CHASE, FRIGHTENED, or EATEN
        self.state = "CHASE"
        self.was_scared = False

        # Eaten / respawn system
        self.respawn_timer = 0.0
        self.RESPAWN_DELAY = 5.0  # seconds before an eaten ghost comes back
        self.normal_texture_path = texture_path

        # Home corner
        self.home_row = None
        self.home_col = None
        self.name = name



    @classmethod
    def create_ghost(
        cls,
        center_x: float,
        center_y: float,
        cell_size: float,
        name: str
    ) -> tuple["Ghost", arcade.SpriteList]:

        ghost_list: arcade.SpriteList = arcade.SpriteList()

        ghost = cls(center_x, center_y, name)

        ghost.width = cell_size * 0.5
        ghost.height = cell_size * 0.5

        ghost_list.append(ghost)

        return ghost, ghost_list

    #Coordinate helpers

    def get_target_tile(
            self,
            player,
            player_row,
            player_col,
            **kwargs
            ):
        """
        Returns the row and column this ghost wants
        to chase.

        Extra context (my_row/my_col, blinky_row/blinky_col) is passed
        via kwargs so each ghost subclass can use only what it needs.
        """

        if self.state == "FRIGHTENED":
            return self.home_row, self.home_col

        return player_row, player_col

    def get_cell(self, x, y, cell_size, rows, offset_x=0.0, offset_y=0.0):
        col = int(round(((x - offset_x) - cell_size / 2) / cell_size))
        row = int(round(((rows - 1) * cell_size + cell_size / 2 - (y - offset_y)) / cell_size))
        return row, col

    def get_cell_center(self, row, col, cell_size, rows, offset_x=0.0, offset_y=0.0):
        x = offset_x + col * cell_size + cell_size / 2
        y = offset_y + (rows - 1 - row) * cell_size + cell_size / 2
        return x, y

    #Pathfinding helpers

    def can_move(self, dir_tuple: tuple[int, int], maze, cell_size: float, rows: int, cols: int,
                 offset_x: float = 0.0, offset_y: float = 0.0) -> bool:
        dx, dy = dir_tuple
        if dx == 0 and dy == 0:
            return False

        col = int(round(((self.center_x - offset_x) - cell_size / 2) / cell_size))
        row = int(round(((rows - 1) * cell_size + cell_size / 2 - (self.center_y - offset_y)) / cell_size))

        col = max(0, min(cols - 1, col))
        row = max(0, min(rows - 1, row))

        cell_val = maze[row][col]

        NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

        if dy == 1 and (cell_val & NORTH):
            return False

        if dy == -1 and (cell_val & SOUTH):
            return False

        if dx == 1 and (cell_val & EAST):
            return False

        if dx == -1 and (cell_val & WEST):
            return False

        return True

    def neighbors(self, row, col, maze, rows, cols):
        NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
        cell_val = maze[row][col]
        result = []
        if not (cell_val & NORTH) and row - 1 >= 0:
            result.append(((row - 1, col), (0, 1)))
        if not (cell_val & SOUTH) and row + 1 < rows:
            result.append(((row + 1, col), (0, -1)))
        if not (cell_val & EAST) and col + 1 < cols:
            result.append(((row, col + 1), (1, 0)))
        if not (cell_val & WEST) and col - 1 >= 0:
            result.append(((row, col - 1), (-1, 0)))
        return result


    def next_direction_bfs(self, start, goal, maze, rows, cols):
        """BFS from start cell to goal cell. Returns the first-step direction."""
        if start == goal:
            return (0, 0)

        visited = {start}
        queue = deque([(start, None)])  # (cell, first_dir_taken)

        while queue:
            (row, col), first_dir = queue.popleft()

            for (nrow, ncol), d in self.neighbors(row, col, maze, rows, cols):
                if (nrow, ncol) in visited:
                    continue
                visited.add((nrow, ncol))
                step_dir = first_dir if first_dir is not None else d

                if (nrow, ncol) == goal:
                    return step_dir

                queue.append(((nrow, ncol), step_dir))

        return (0, 0)


    #Eaten / respawn system

    def get_hit(self) -> None:
        """Called when Pac-Man eats this ghost while it's FRIGHTENED."""
        self.state = "EATEN"
        self.respawn_timer = self.RESPAWN_DELAY
        self.visible = False
        self.current_dir = (0, 0)

    def update_eaten(self,
                      delta_time: float,
                      cell_size: float,
                      rows: int,
                      offset_x: float = 0.0,
                      offset_y: float = 0.0) -> None:
        """Counts down while the ghost is eaten, then respawns it at home."""
        self.respawn_timer -= delta_time
        if self.respawn_timer <= 0:
            x, y = self.get_cell_center(self.home_row, self.home_col, cell_size, rows, offset_x, offset_y)
            self.center_x = self.target_x = x
            self.center_y = self.target_y = y
            self.state = "CHASE"
            self.visible = True
            self.texture = arcade.load_texture(self.normal_texture_path)

    #chase the player through the maze.
    def chase_player(self,
                     player: Player,
                     maze,
                     cell_size: float,
                     rows: int,
                     cols: int,
                     offset_x: float = 0.0,
                     offset_y: float = 0.0,
                     delta_time: float = 1 / 60,
                     blinky: "Ghost" = None
                     ) -> None:

        if self.state == "EATEN":
            self.update_eaten(delta_time, cell_size, rows, offset_x, offset_y)
            return

        step = self.speed * delta_time

        if player.is_powered_up and self.state == "CHASE":
            self.state = "FRIGHTENED"
            self.texture = arcade.load_texture(SCARED_PATH)
        elif not player.is_powered_up and self.state == "FRIGHTENED":
            self.state = "CHASE"
            self.texture = arcade.load_texture(self.normal_texture_path)

        # Snap to target when close enough to avoid float jitter.
        if abs(self.center_x - self.target_x) <= step and abs(self.center_y - self.target_y) <= step:
            self.center_x = self.target_x
            self.center_y = self.target_y

        # Arrived at a cell center -> pick next direction via BFS.
        if self.center_x == self.target_x and self.center_y == self.target_y:
            my_row, my_col = self.get_cell(self.center_x, self.center_y, cell_size, rows, offset_x, offset_y)

            player_row, player_col = self.get_cell(player.center_x, player.center_y, cell_size, rows, offset_x, offset_y)

            my_row = max(0, min(rows - 1, my_row))
            my_col = max(0, min(cols - 1, my_col))
            player_row = max(0, min(rows - 1, player_row))
            player_col = max(0, min(cols - 1, player_col))

            blinky_row = blinky_col = None
            if blinky is not None:
                blinky_row, blinky_col = self.get_cell(
                    blinky.center_x, blinky.center_y, cell_size, rows, offset_x, offset_y
                )
                blinky_row = max(0, min(rows - 1, blinky_row))
                blinky_col = max(0, min(cols - 1, blinky_col))

            target_row, target_col = self.get_target_tile(
                player,
                player_row,
                player_col,
                my_row=my_row,
                my_col=my_col,
                blinky_row=blinky_row,
                blinky_col=blinky_col,
                maze=maze,
                rows=rows,
                cols=cols,
            )

        
            target_row = max(0, min(rows - 1, target_row))
            target_col = max(0, min(cols - 1, target_col))

            self.current_dir = self.next_direction_bfs(
                (my_row, my_col),
                (target_row, target_col),
                maze,
                rows,
                cols,
            )

            if self.current_dir != (0, 0):
                self.target_x = self.center_x + self.current_dir[0] * cell_size
                self.target_y = self.center_y + self.current_dir[1] * cell_size

        # Move toward target.
        if self.center_x < self.target_x:
            self.center_x = min(self.target_x, self.center_x + step)
        elif self.center_x > self.target_x:
            self.center_x = max(self.target_x, self.center_x - step)

        if self.center_y < self.target_y:
            self.center_y = min(self.target_y, self.center_y + step)
        elif self.center_y > self.target_y:
            self.center_y = max(self.target_y, self.center_y - step)

        if self.center_y == self.target_y and self.center_x == self.target_x:
            self.center_x = min(self.target_x, self.center_x + step)


class Blinky(Ghost):
    def __init__(self, center_x, center_y, name: str):
        super().__init__(center_x, center_y, texture_path=BLINKY_PATH, name=name)


    # def get_target_tile(self, player_row, player_col):

    #     return super().get_target_tile(
    #         player_row,
    #         player_col,
    #     )


class Pinky(Ghost):
    """Ambush: always aims a few tiles ahead of Pac-Man's current heading."""

    AMBUSH_DISTANCE = 4
    AMBUSH_CHANCE = 0.5

    def __init__(self, center_x, center_y, name: str):
        super().__init__(center_x, center_y, texture_path=PINKY_PATH, name=name)

    def get_target_tile(self, player, player_row, player_col, **kwargs):

        if self.state == "FRIGHTENED":
            return self.home_row, self.home_col

        dx, dy = player.current_dir

        if dx == 0 and dy == 0:
            return player_row, player_col

        target_row = player_row - dy * self.AMBUSH_DISTANCE
        target_col = player_col + dx * self.AMBUSH_DISTANCE

        return target_row, target_col


class Inky(Ghost):

    AMBUSH_DISTANCE = 4
    AMBUSH_CHANCE = 0.5

    def __init__(self, center_x, center_y, name: str):
        super().__init__(center_x, center_y, texture_path=INKY_PATH, name=name)

    def get_target_tile(self, player, player_row, player_col, **kwargs):

        if self.state == "FRIGHTENED":
            return self.home_row, self.home_col

        dx, dy = player.current_dir

        if random.random() < self.AMBUSH_CHANCE and (dx != 0 or dy != 0):
            target_row = player_row - dy * self.AMBUSH_DISTANCE
            target_col = player_col + dx * self.AMBUSH_DISTANCE
            return target_row, target_col

        return player_row, player_col


class Clyde(Ghost):


    def __init__(self, center_x, center_y, name: str):
        super().__init__(center_x, center_y, texture_path=CLYDE_PATH, name=name)

    def get_target_tile(self, player, player_row, player_col, **kwargs):

        if self.state == "FRIGHTENED":
            return self.home_row, self.home_col

        rows = kwargs.get("rows")
        cols = kwargs.get("cols")

        if not rows or not cols:
            return player_row, player_col

        return random.randrange(rows), random.randrange(cols)




