import pathlib
import arcade

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
ASSETS_PATH = SCRIPT_DIR / "assets" / "Group.png"


class Player(arcade.Sprite):
    def __init__(self, center_x: float, center_y: float, speed: float) -> None:
        super().__init__(str(ASSETS_PATH))
        self.center_x = center_x
        self.center_y = center_y
        self.target_x = center_x
        self.target_y = center_y
        self.speed = speed
        self.queued_dir = (0, 0)
        self.current_dir = (0, 0)

        #Power-Up System
        self.is_powered_up = False
        self.power_timer = 0.0

        #Lives / damage system
        self.lives = 3
        self.invincible = False
        self.invincible_timer = 0.0
        self.INVINCIBILITY_DURATION = 2.0  # seconds of grace after respawning

    def take_damage(self) -> bool:
        """Removes one life, starts invincibility. Returns True if game over."""
        if self.invincible:
            return False
        self.lives -= 1
        self.invincible = True
        self.invincible_timer = self.INVINCIBILITY_DURATION
        return self.lives <= 0

    def respawn_at(self, x: float, y: float) -> None:
        """Resets position/movement state after losing a life."""
        self.center_x = x
        self.center_y = y
        self.target_x = x
        self.target_y = y
        self.current_dir = (0, 0)
        self.queued_dir = (0, 0)

    def update_invincibility(self, delta_time: float) -> None:
        if self.invincible:
            self.invincible_timer -= delta_time
            if self.invincible_timer <= 0:
                self.invincible = False
                self.invincible_timer = 0.0

    @staticmethod
    def create_player(
        center_x: float, center_y: float, cell_size: float, speed: float = 170.0
    ) -> tuple["Player", arcade.SpriteList]:
        player_list: arcade.SpriteList = arcade.SpriteList()

        player = Player(center_x, center_y, speed)
        player.width = cell_size * 0.5
        player.height = cell_size * 0.5
        player_list.append(player)

        return player, player_list

    def on_key_press(self, key: int):
        if key == arcade.key.UP:
            self.queued_dir = (0, 1)
        elif key == arcade.key.DOWN:
            self.queued_dir = (0, -1)
        elif key == arcade.key.LEFT:
            self.queued_dir = (-1, 0)
        elif key == arcade.key.RIGHT:
            self.queued_dir = (1, 0)

    def on_key_release(self, key: int):
        pass

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

    def activate_power_up(self, duration: float = 10.0):
        """Triggers the power-up state and resets/starts the duration clock."""
        self.is_powered_up = True
        self.power_timer = duration

    def update_grid_movement(self,
                             maze,
                             cell_size: float,
                             rows: int,
                             cols: int,
                             offset_x: float = 0.0,
                             offset_y: float = 0.0,
                             delta_time: float = 1 / 60
                             ) -> None:

        if self.is_powered_up:
            self.power_timer -= delta_time
            if self.power_timer <= 0:
                self.is_powered_up = False
                self.power_timer = 0.0

        self.update_invincibility(delta_time)


        current_speed = self.speed * 2.0 if self.is_powered_up else self.speed
        step = current_speed * delta_time


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


