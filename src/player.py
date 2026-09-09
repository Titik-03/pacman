import pathlib
from typing import Any
import arcade

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
ASSETS_PATH = "src/assets/Untitled/5.png"


class Player(arcade.Sprite):
    """Player character sprite handling movement, lives, and animations."""

    def __init__(self, center_x: float, center_y: float, speed: float) -> None:
        """Initialize player position, speed, textures, and animation state."""
        super().__init__(str(ASSETS_PATH))
        self.center_x = center_x
        self.center_y = center_y
        self.target_x = center_x
        self.target_y = center_y
        self.speed = speed
        self.queued_dir = (0, 0)
        self.current_dir = (0, 0)
        self.textures_open = arcade.load_texture("src/assets/Untitled/6.png")
        self.textures_half = arcade.load_texture("src/assets/Untitled/4.png")
        self.textures_closed = arcade.load_texture("src/assets/Untitled/5.png")
        self.animation_frames = [
            self.textures_open,
            self.textures_half,
            self.textures_closed,
            self.textures_half
        ]
        self.death_crack = arcade.load_texture("src/assets/death/8.png")
        self.death_start = arcade.load_texture("src/assets/death/Group 13.png")
        self.death_middle = arcade.load_texture(
            "src/assets/death/Group 14.png")
        self.death_end = arcade.load_texture("src/assets/death/Group 15.png")
        self.death_shatter = arcade.load_texture(
            "src/assets/death/Group 16.png")
        self.death_animation = [
            self.death_crack,
            self.death_start,
            self.death_middle,
            self.death_end,
            self.death_shatter,
        ]
        self.is_dying = False
        self.death_frame_index = 0
        self.death_timer = 0.0
        self.death_frame_duration = 0.15
        self.cur_frame_index = 0
        self.time_counter = 0.0
        self.frame_duration = 0.08
        self.is_powered_up = False
        self.power_timer = 0.0
        self.just_took_damage = False
        self.just_started = True
        self.damage_invincibility_duration = 2.0

        self.lives = 3
        self.invincible = False
        self.invincible_cheat = False
        self.invincible_timer = 0.0
        # self.INVINCIBILITY_DURATION = 2.0
        self.current_speed = self.speed

    def start_death_animation(self) -> None:
        """Starts the death animation sequence."""
        self.is_dying = True
        self.death_frame_index = 0
        self.death_timer = 0.0
        self.texture = self.death_animation[0]
        self.angle = 0

    def queue_direction(self, dir_tuple: tuple[int, int]) -> None:
        """Sets the queued movement direction directly
        (used by Level 5 text commands).
        """
        if not self.is_dying:
            self.queued_dir = dir_tuple

    def take_damage(self) -> bool:
        """Removes one life, starts invincibility.
        Returns True if game over.
        """
        if self.invincible:
            return False
        self.lives -= 1
        self.invincible = True
        self.is_powered_up = False
        self.power_timer = 0.0
        self.damage_invincibility_duration = 2.0
        self.invincible_timer = 2.0
        self.just_took_damage = True
        return self.lives <= 0

    def respawn_at(self, x: float, y: float) -> None:
        """Resets position/movement state after losing a life."""
        self.center_x = x
        self.center_y = y
        self.target_x = x
        self.target_y = y
        self.current_dir = (0, 0)
        self.queued_dir = (0, 0)
        self.is_dying = False
        self.death_frame_index = 0
        self.death_timer = 0.0
        self.texture = self.animation_frames[0]
        self.angle = 0
        self.visible = True
        self.just_started = True

    def update_invincibility(self, delta_time: float) -> None:
        """Update invincibility timer and flashing alpha effect."""

        if self.is_dying:
            self.alpha = 255
            return

        if self.invincible:
            self.invincible_timer -= delta_time

            if self.just_took_damage:
                # start flashing.
                if int(self.invincible_timer * 15) % 2 == 0:
                    self.alpha = 255
                else:
                    self.alpha = 0

                # stop flashing.
                if self.invincible_timer <= 0:
                    self.just_took_damage = False
                    self.alpha = 255
                    if not self.invincible_cheat:
                        self.invincible = False
                        self.invincible_timer = 0.0
            else:
                self.alpha = 255
                if self.invincible_timer <= 0 and not self.invincible_cheat:
                    self.invincible = False
                    self.invincible_timer = 0.0
        else:
            self.alpha = 255

    @staticmethod
    def create_player(
        center_x: float,
        center_y: float,
        cell_size: float,
        speed: float = 180.0,
    ) -> tuple["Player", arcade.SpriteList]:
        """Create and configure a Player sprite and its container list."""
        player_list: arcade.SpriteList = arcade.SpriteList()

        player = Player(center_x, center_y, speed)
        player.width = cell_size * 0.5
        player.height = cell_size * 0.5
        player_list.append(player)

        return player, player_list

    def on_key_press(self, key: int) -> None:
        """Queue movement direction based on directional key press."""
        if self.is_dying:
            return
        if key == arcade.key.UP or key == arcade.key.W:
            self.queued_dir = (0, 1)
            self.just_started = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.queued_dir = (0, -1)
            self.just_started = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.queued_dir = (-1, 0)
            self.just_started = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.queued_dir = (1, 0)
            self.just_started = False

    def on_key_release(self, key: int) -> None:
        """Handle key release events for the player."""
        pass

    def can_move(
        self,
        dir_tuple: tuple[int, int],
        maze: list[list[int]],
        cell_size: float,
        rows: int,
        cols: int,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
    ) -> bool:
        """Check if player can move in direction without hitting a wall."""
        dx, dy = dir_tuple
        if dx == 0 and dy == 0:
            return False

        col = int(
            round(((self.center_x - offset_x) - cell_size / 2) / cell_size)
        )
        row = int(round(((rows - 1) * cell_size + cell_size /
                  2 - (self.center_y - offset_y)) / cell_size))

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
            self.angle = 0
        if dx == -1 and (cell_val & WEST):
            return False

        return True

    def activate_power_up(self, duration: float = 10.0) -> None:
        """Triggers the power-up state and resets/starts the duration clock."""
        self.is_powered_up = True
        self.power_timer = duration

    def update_animation(
        self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any
    ) -> None:
        """Advance walk or death animation frames and flip textures."""
        if self.is_dying:
            self.death_timer += delta_time
            if self.death_timer >= self.death_frame_duration:
                self.death_timer = 0.0
                self.death_frame_index += 1
                if self.death_frame_index < len(self.death_animation):
                    self.texture = self.death_animation[self.death_frame_index]
                else:
                    self.is_dying = False
            return

        if self.current_dir != (0, 0):
            self.time_counter += delta_time
            if self.time_counter >= self.frame_duration:
                self.time_counter = 0.0
                self.cur_frame_index = (
                    self.cur_frame_index + 1) % len(self.animation_frames)
                frame_tex = self.animation_frames[self.cur_frame_index]
                self.texture = frame_tex.flip_left_right(
                ) if self.current_dir[0] < 0 else frame_tex
        else:
            base_tex = self.animation_frames[0]
            self.texture = base_tex.flip_left_right(
            ) if self.queued_dir[0] < 0 else base_tex

    def update_grid_movement(self,
                             maze: list[list[int]],
                             cell_size: float,
                             rows: int,
                             cols: int,
                             offset_x: float = 0.0,
                             offset_y: float = 0.0,
                             delta_time: float = 1 / 60,
                             ignore_power_up_speed: bool = False,
                             ) -> None:
        """Update tile-based grid movement toward the target cell."""

        if self.is_powered_up:
            self.power_timer -= delta_time
            if self.power_timer <= 0:
                self.is_powered_up = False
                self.power_timer = 0.0

        self.update_invincibility(delta_time)

        self.damage_invincibility_duration -= delta_time
        if self.damage_invincibility_duration <= 0:
            self.damage_invincibility_duration = 0.0
            self.just_took_damage = False

        self.current_speed = (
            self.speed
            if ignore_power_up_speed
            else (self.speed * 1.6 if self.is_powered_up else self.speed)
        )
        step = self.current_speed * delta_time

        if (
            abs(self.center_x - self.target_x) <= step
            and abs(self.center_y - self.target_y) <= step
        ):
            self.center_x = self.target_x
            self.center_y = self.target_y

        # Arrived at cell center -> evaluate next move.
        if self.center_x == self.target_x and self.center_y == self.target_y:
            if self.can_move(
                self.queued_dir,
                maze,
                cell_size,
                rows,
                cols,
                offset_x,
                offset_y,
            ):
                self.current_dir = self.queued_dir

            elif not self.can_move(
                self.current_dir,
                maze,
                cell_size,
                rows,
                cols,
                offset_x,
                offset_y,
            ):
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
