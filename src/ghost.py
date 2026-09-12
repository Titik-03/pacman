from typing import Any
from arcade.types import Color
from src.player import Player
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
EYES_PATH = SCRIPT_DIR / "assets" / "eyes.png"

EYES_PATH = SCRIPT_DIR / "assets" / "eyes.png"


class Ghost(arcade.Sprite):
    """Base ghost sprite handling AI pathfinding, states, and textures."""

    def __init__(
        self,
        center_x: float,
        center_y: float,
        name: str = "",
        texture_path: Any = None,
    ) -> None:
        """Initialize ghost position, AI state, timers, and textures."""
        super().__init__(path_or_texture=texture_path)
        self.center_x = center_x
        self.center_y = center_y
        self.target_x = center_x
        self.target_y = center_y
        self.speed = 115.0
        self.og_speed = 115.0
        self.og_speed = 115.0
        self.current_dir = (0, 0)

        # Power-Up System
        self.is_powered_up = False
        # # self.power_timer = 0.0

        # Ghost state: CHASE, FRIGHTENED, or EATEN
        self.state = "CHASE"
        self.was_scared = False
        self.was_eaten = False
        self.can_damage = True
        self.was_eaten = False
        self.can_damage = True

        # Eaten / respawn system
        self.respawn_timer = 0.0
        self.RESPAWN_DELAY = 5.0  # seconds before an eaten ghost comes back
        self.normal_texture_path = texture_path

        # Home corner
        self.home_row: Any = None
        self.home_col: Any = None
        self.name = name
        self.target_tile: Any = None

    @classmethod
    def create_ghost(
        cls,
        center_x: float,
        center_y: float,
        cell_size: float,
        name: str
    ) -> tuple["Ghost", arcade.SpriteList]:
        """Create and configure a Ghost sprite and its container list."""
        ghost_list: arcade.SpriteList = arcade.SpriteList()

        ghost = cls(center_x, center_y, name)

        ghost.width = cell_size * 0.65
        ghost.height = cell_size * 0.65

        ghost_list.append(ghost)

        return ghost, ghost_list

    # Coordinate helpers

    def get_target_tile(
        self,
        player: Any,
        player_row: int,
        player_col: int,
        **kwargs: Any,
    ) -> tuple[int, int]:
        """
        Returns the row and column this ghost wants
        to chase.

        Extra context (my_row/my_col, blinky_row/blinky_col) is passed
        via kwargs so each ghost subclass can use only what it needs.
        """

        if self.state == "FRIGHTENED":
            my_row = kwargs.get("my_row")
            my_col = kwargs.get("my_col")

            # safe check.
            if my_row is None or my_col is None:
                return self.home_row, self.home_col

            diff_row = my_row - player_row
            diff_col = my_col - player_col

            # if diff_row == 0 and diff_col == 0:
            #     return self.home_row, self.home_col

            # opposite direction.
            target_row = my_row + (diff_row)
            target_col = my_col + (diff_col)

            return target_row, target_col

        return player_row, player_col

    def get_cell(
        self,
        x: float,
        y: float,
        cell_size: float,
        rows: int,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
    ) -> tuple[int, int]:
        """Convert screen coordinates to maze grid row and column."""
        col = int(round(((x - offset_x) - cell_size / 2) / cell_size))
        row = int(
            round(
                ((rows - 1) * cell_size + cell_size / 2 - (y - offset_y))
                / cell_size
            )
        )
        return row, col

    def get_cell_center(
        self,
        row: int,
        col: int,
        cell_size: float,
        rows: int,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
    ) -> tuple[float, float]:
        """Convert maze grid row and column to screen coordinates."""
        x = offset_x + col * cell_size + cell_size / 2
        y = offset_y + (rows - 1 - row) * cell_size + cell_size / 2
        return x, y

    def neighbors(
        self,
        row: int,
        col: int,
        maze: list[list[int]],
        rows: int,
        cols: int,
    ) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """Return reachable neighboring tiles and direction vectors."""
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

    def next_direction_bfs(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
        maze: list[list[int]],
        rows: int,
        cols: int,
    ) -> tuple[int, int]:
        """BFS from start cell to goal cell.
        Returns the first-step direction.
        """
        if start == goal:
            return (0, 0)

        visited = {start}
        queue: deque[tuple[tuple[int, int], tuple[int, int] | None]] = deque(
            [(start, None)]
        )  # (cell, first_dir_taken)

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

    def get_hit(self) -> None:
        """Called when Pac-Man eats this ghost while it's FRIGHTENED."""
        self.state = "EATEN"
        self.can_damage = True
        self.texture = arcade.load_texture(EYES_PATH)

    def update_texrture(self, player: Player) -> None:
        """Update ghost texture and tint based on state and player power."""
        if self.state == "EATEN":
            return

        if player.is_powered_up:
            if self.state == "CHASE":
                self.state = "FRIGHTENED"
                self.texture = arcade.load_texture(SCARED_PATH)

            if self.state == "FRIGHTENED":
                if player.power_timer <= 3.0:
                    is_white_frame = int(player.power_timer * 6.5) % 2 == 0
                    self.color = (255, 255, 255) if is_white_frame else (
                        137, 180, 250)
                else:
                    self.color = (255, 255, 255)
            return

        if self.state == "FRIGHTENED":
            self.state = "CHASE"
            self.texture = arcade.load_texture(self.normal_texture_path)

        self.color = (255, 255, 255)
        self.was_eaten = False

    def draw_target_x(
        self,
        cell_size: float,
        offset_x: float,
        offset_y: float,
        rows: int,
        color: tuple[int, int, int] | Color = arcade.color.RED,
        size: float = 10,
        line_width: float = 3,
    ) -> None:
        """Draw debug line and marker toward the ghost's target tile."""
        if hasattr(self, "target_tile") and self.target_tile:
            target_row, target_col = self.target_tile

            # Convert (row, col) to Screen (x, y) center position
            target_x = offset_x + (target_col + 0.5) * cell_size
            target_y = offset_y + (rows - 1 - target_row + 0.5) * cell_size

            if self.state == "FRIGHTENED":
                color = arcade.color.BLUE

            arcade.draw_line(
                self.center_x, self.center_y,
                target_x, target_y,
                color, line_width=2
            )

            arcade.draw_line(
                target_x - size, target_y - size,
                target_x + size, target_y + size,
                color, line_width
            )
            arcade.draw_line(
                target_x - size, target_y + size,
                target_x + size, target_y - size,
                color, line_width
            )

    # chase the player.
    def chase_player(self,
                     player: Player,
                     maze: list[list[int]],
                     cell_size: float,
                     rows: int,
                     cols: int,
                     offset_x: float = 0.0,
                     offset_y: float = 0.0,
                     delta_time: float = 1 / 60,
                     blinky: "Ghost | None" = None
                     ) -> None:
        """Advance ghost AI pathfinding and grid movement for one frame."""

        if player.power_timer == 0:
            self.was_eaten = False
            self.can_damage = True
            self.visible = True

        my_row, my_col = self.get_cell(
            self.center_x,
            self.center_y,
            cell_size,
            rows,
            offset_x,
            offset_y,
        )

        if (
            self.was_eaten
            and my_row == self.home_row
            and my_col == self.home_col
        ):
            self.texture = arcade.load_texture(EYES_PATH)

        if self.was_eaten and player.power_timer != 0:
            return

        # Let the ghost move twice as fast when returning as eyes
        current_speed = (
            self.speed * 2.0 if self.state == "EATEN" else self.speed
        )
        step = current_speed * delta_time

        self.update_texrture(player)

        # Snap to target when close enough to avoid float jitter.
        if (
            abs(self.center_x - self.target_x) <= step
            and abs(self.center_y - self.target_y) <= step
        ):
            self.center_x = self.target_x
            self.center_y = self.target_y

        # Arrived at a cell center -> pick next direction via BFS.
        if self.center_x == self.target_x and self.center_y == self.target_y:
            my_row, my_col = self.get_cell(
                self.center_x,
                self.center_y,
                cell_size,
                rows,
                offset_x,
                offset_y,
            )

            # If we are eaten and have arrived at our home cell,
            # turn back into a normal ghost
            if player.power_timer == 0:
                if (
                    self.state == "EATEN"
                    and my_row == self.home_row
                    and my_col == self.home_col
                ):
                    self.state = "CHASE"
                    self.texture = arcade.load_texture(
                        self.normal_texture_path)
                    self.was_eaten = True

            player_row, player_col = self.get_cell(
                player.center_x,
                player.center_y,
                cell_size,
                rows,
                offset_x,
                offset_y,
            )

            my_row = max(0, min(rows - 1, my_row))
            my_col = max(0, min(cols - 1, my_col))
            player_row = max(0, min(rows - 1, player_row))
            player_col = max(0, min(cols - 1, player_col))

            blinky_row = blinky_col = None
            if blinky is not None:
                blinky_row, blinky_col = self.get_cell(
                    blinky.center_x,
                    blinky.center_y,
                    cell_size,
                    rows,
                    offset_x,
                    offset_y,
                )
                blinky_row = max(0, min(rows - 1, blinky_row))
                blinky_col = max(0, min(cols - 1, blinky_col))

            # choose where to go.
            if self.state == "FRIGHTENED":
                valid_moves = self.neighbors(my_row, my_col, maze, rows, cols)
                reverse_dir = (-self.current_dir[0], -self.current_dir[1])

                # dont go to the same way you came from.
                if len(valid_moves) > 1:
                    forward_moves = [
                        m for m in valid_moves if m[1] != reverse_dir]
                    if forward_moves:
                        valid_moves = forward_moves

                # chose tile that keeps ghost away from player.
                best_dir = (0, 0)
                max_dist = -1

                for (nrow, ncol), d in valid_moves:
                    dist = abs(nrow - player_row) + abs(ncol - player_col)
                    if dist > max_dist:
                        max_dist = dist
                        best_dir = d
                        best_tile = (nrow, ncol)

                self.current_dir = best_dir
                self.target_tile = best_tile

            else:
                if self.state == "EATEN":
                    target_row = self.home_row
                    target_col = self.home_col
                else:
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

                self.target_tile = (target_row, target_col)

                # Prevent the ghost from stopping on the player when chasing
                if self.current_dir == (0, 0) and self.state == "CHASE":
                    valid_moves = self.neighbors(
                        my_row, my_col, maze, rows, cols)
                    if valid_moves:
                        import random
                        random_move = random.choice(valid_moves)
                        self.current_dir = random_move[1]

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
    """Red ghost (Blinky) directly targeting Pac-Man."""

    def __init__(self, center_x: float, center_y: float, name: str) -> None:
        """Initialize Blinky with red texture and corner position."""
        super().__init__(
            center_x, center_y, texture_path=BLINKY_PATH, name=name
        )


class Pinky(Ghost):
    """Ambush: always aims a few tiles ahead of Pac-Man's current heading."""

    AMBUSH_DISTANCE = 4
    AMBUSH_CHANCE = 0.5

    def __init__(self, center_x: float, center_y: float, name: str) -> None:
        """Initialize Pinky with pink texture and corner position."""
        super().__init__(
            center_x, center_y, texture_path=PINKY_PATH, name=name
        )

    def get_target_tile(
        self, player: Any, player_row: int, player_col: int, **kwargs: Any
    ) -> tuple[int, int]:
        """Target a position ahead of Pac-Man to ambush."""
        if self.state == "FRIGHTENED":
            my_row = kwargs.get("my_row")
            my_col = kwargs.get("my_col")

            # safe check.
            if my_row is None or my_col is None:
                return self.home_row, self.home_col

            diff_row = my_row - player_row
            diff_col = my_col - player_col

            if diff_row == 0 and diff_col == 0:
                return self.home_row, self.home_col

            # opposite direction.
            target_row = my_row + (diff_row * 20)
            target_col = my_col + (diff_col * 20)

            return target_row, target_col

        dx, dy = player.current_dir

        if dx == 0 and dy == 0:
            return player_row, player_col

        target_row = player_row - dy * self.AMBUSH_DISTANCE
        target_col = player_col + dx * self.AMBUSH_DISTANCE

        return target_row, target_col


class Inky(Ghost):
    """Cyan ghost (Inky) with unpredictable targeting behavior."""

    AMBUSH_DISTANCE = 4
    AMBUSH_CHANCE = 0.5

    def __init__(self, center_x: float, center_y: float, name: str) -> None:
        """Initialize Inky with cyan texture and corner position."""
        super().__init__(center_x, center_y, texture_path=INKY_PATH, name=name)

    def get_target_tile(
        self, player: Any, player_row: int, player_col: int, **kwargs: Any
    ) -> tuple[int, int]:
        """Target Pac-Man or ambush based on a random chance."""
        if self.state == "FRIGHTENED":
            my_row = kwargs.get("my_row")
            my_col = kwargs.get("my_col")

            # safe check.
            if my_row is None or my_col is None:
                return self.home_row, self.home_col

            diff_row = my_row - player_row
            diff_col = my_col - player_col

            if diff_row == 0 and diff_col == 0:
                return self.home_row, self.home_col

            # opposite direction.
            target_row = my_row + (diff_row * 20)
            target_col = my_col + (diff_col * 20)

            return target_row, target_col

        dx, dy = player.current_dir

        if random.random() < self.AMBUSH_CHANCE and (dx != 0 or dy != 0):
            target_row = player_row - dy * self.AMBUSH_DISTANCE
            target_col = player_col + dx * self.AMBUSH_DISTANCE
            return target_row, target_col

        return player_row, player_col


class Clyde(Ghost):
    """Orange ghost (Clyde) with random movement behavior."""

    def __init__(self, center_x: float, center_y: float, name: str) -> None:
        """Initialize Clyde with orange texture and corner position."""
        super().__init__(
            center_x, center_y, texture_path=CLYDE_PATH, name=name
        )

    def get_target_tile(
        self, player: Any, player_row: int, player_col: int, **kwargs: Any
    ) -> tuple[int, int]:
        """Target random tiles across the maze."""

        if self.state == "FRIGHTENED":
            my_row = kwargs.get("my_row")
            my_col = kwargs.get("my_col")

            # safe check.
            if my_row is None or my_col is None:
                return self.home_row, self.home_col

            diff_row = my_row - player_row
            diff_col = my_col - player_col

            if diff_row == 0 and diff_col == 0:
                return self.home_row, self.home_col

            # opposite direction.
            target_row = my_row + (diff_row * 20)
            target_col = my_col + (diff_col * 20)

            return target_row, target_col

        rows = kwargs.get("rows")
        cols = kwargs.get("cols")

        if not rows or not cols:
            return player_row, player_col

        return random.randrange(rows), random.randrange(cols)
