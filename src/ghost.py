import pathlib
import arcade

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
ASSETS_PATH = SCRIPT_DIR / "assets" / "Group.png"


class Ghost(arcade.Sprite):
    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(str(ASSETS_PATH))
        self.center_x = center_x
        self.center_y = center_y
        self.target_x = center_x
        self.target_y = center_y
        self.speed = 180.0
        self.queued_dir = (0, 0)
        self.current_dir = (0, 0)
        
        #Power-Up System
        self.is_powered_up = False
        self.power_timer = 0.0

    @staticmethod
    def create_player(
        center_x: float, center_y: float, cell_size: float
    ) -> tuple["Ghost", arcade.SpriteList]:
        player_list: arcade.SpriteList = arcade.SpriteList()

        ghost = Ghost(center_x, center_y)
        ghost.width = cell_size * 0.5
        ghost.height = cell_size * 0.5
        player_list.append(ghost)

        return ghost

    # def on_key_press(self, key: int):
    #     if key == arcade.key.UP:
    #         self.queued_dir = (0, 1)
    #     elif key == arcade.key.DOWN:
    #         self.queued_dir = (0, -1)
    #     elif key == arcade.key.LEFT:
    #         self.queued_dir = (-1, 0)
    #     elif key == arcade.key.RIGHT:
    #         self.queued_dir = (1, 0)

    # def on_key_release(self, key: int):
    #     pass

    def can_move(self, dir_tuple: tuple[int, int], maze, cell_size: float, rows: int, cols: int, offset_x: float = 0.0, offset_y: float = 0.0) -> bool:
        dx, dy = dir_tuple
        if dx == 0 and dy == 0:
            return False

        col = int(round(((self.center_x - offset_x) - cell_size / 2) / cell_size))
        row = int(round(((rows - 1) * cell_size + cell_size / 2 - (self.center_y - offset_y)) / cell_size))

        col = max(0, min(cols - 1, col))
        row = max(0, min(rows - 1, row))

        cell_val = maze[row][col]

        NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

        if dy == 1:
            self.angle = 270
        if dy == 1 and (cell_val & NORTH):
            return False

        if dy == -1:
            self.angle = 90
        if dy == -1 and (cell_val & SOUTH):
            return False

        if dx == 1:
            self.angle = 0
        if dx == 1 and (cell_val & EAST):
            return False

        elif dx == -1:
            self.angle = 180
        if dx == -1 and (cell_val & WEST):
            return False

        return True

    def update_grid_movement(self,
                             maze,
                             cell_size: float,
                             rows: int,
                             cols: int,
                             offset_x: float = 0.0,
                             offset_y: float = 0.0,
                             delta_time: float = 1 / 60
                             ) -> None:

        #Tick down the power-up timer
        if self.is_powered_up:
            self.power_timer -= delta_time
            if self.power_timer <= 0:
                self.is_powered_up = False
                self.power_timer = 0.0

        #Calculate dynamic speed
        current_speed = self.speed * 2.0 if self.is_powered_up else self.speed
        step = current_speed * delta_time

        # Snap to the target when we are close enough to avoid float jitter.
        if abs(self.center_x - self.target_x) <= step and abs(self.center_y - self.target_y) <= step:
            self.center_x = self.target_x
            self.center_y = self.target_y

        # Arrived at cell center -> evaluate next move.
        if self.center_x == self.target_x and self.center_y == self.target_y:
            if self.can_move(self.queued_dir, maze, cell_size, rows, cols, offset_x, offset_y):
                self.current_dir = self.queued_dir

            elif not self.can_move(self.current_dir, maze, cell_size, rows, cols, offset_x, offset_y):
                self.current_dir = (0, 0)

            if self.current_dir != (0, 0):
                self.target_x = self.center_x + self.current_dir[0] * cell_size
                self.target_y = self.center_y + self.current_dir[1] * cell_size

        if self.center_x < self.target_x:
            self.center_x = min(self.target_x, self.center_x + step)
        elif self.center_x > self.target_x:
            self.center_x = max(self.target_x, self.center_x - step)

        if self.center_y < self.target_y:
            self.center_y = min(self.target_y, self.center_y + step)
        elif self.center_y > self.target_y:
            self.center_y = max(self.target_y, self.center_y - step)


