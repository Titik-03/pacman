import json
import math
import random
from pathlib import Path
from typing import Any
import PIL.Image
import PIL.ImageDraw

import arcade


class ConfigError(Exception):
    """Raised when the game configuration is invalid."""


class ConfigParser:
    """Loads and validates the JSON game configuration."""

    REQUIRED_KEYS = {
        "level",
        "width",
        "height",
        "lives",
        "pacgum",
        "points_per_pacgum",
        "points_per_super_pacgum",
        "points_per_ghost",
        "seed",
        "level_max_time",
    }

    def __init__(self, filename: str = "src/jsons/config.json") -> None:
        self.filename = Path(filename)
        self.levels: list[dict[str, Any]] = []
        self.highscore_filename = "src/outputs/high_score.json"
        self.load()

    def load(self) -> None:
        """Read, parse and validate the configuration."""
        if not self.filename.exists():
            raise ConfigError(
                f"Configuration file not found: {self.filename}"
            )

        content = self.read_file()

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise ConfigError("Invalid configuration file.")

        self.validate_root(data)
        self.highscore_filename = data.get(
            "highscore_filename",
            "src/outputs/high_score.json",
        )

        if (
            not isinstance(self.highscore_filename, str)
            or not self.highscore_filename
        ):
            raise ConfigError(
                "'highscore_filename' must be a non-empty string."
            )

        levels = data["levels"]
        used_levels: set[int] = set()

        for index, level in enumerate(levels, start=1):
            self.validate_level(level, index)
            level_number = level["level"]

            if level_number in used_levels:
                raise ConfigError(
                    f"Duplicate level number: {level_number}"
                )

            used_levels.add(level_number)

        self.levels = levels

    def read_file(self) -> str:
        """Read the file and ignore lines beginning with # or //."""
        lines = []

        try:
            with self.filename.open("r", encoding="utf-8") as file:
                for line in file:
                    stripped = line.strip()

                    if stripped.startswith("#"):
                        continue
                    if stripped.startswith("//"):
                        continue

                    lines.append(line)
        except OSError:
            raise ConfigError(
                f"Cannot read {self.filename}")

        return "".join(lines)

    def validate_root(self, data: object) -> None:
        """Validate the root configuration object."""
        if not isinstance(data, dict):
            raise ConfigError("The configuration root must be an object.")

        if "levels" not in data:
            raise ConfigError("Missing required key: 'levels'.")

        if not isinstance(data["levels"], list):
            raise ConfigError("'levels' must be an array.")

        if not data["levels"]:
            raise ConfigError("'levels' cannot be empty.")

    def validate_level(self, level: object, index: int) -> None:
        """Validate one level configuration."""
        if not isinstance(level, dict):
            raise ConfigError(f"Level {index} must be an object.")

        missing = self.REQUIRED_KEYS - level.keys()
        if missing:
            keys = ", ".join(sorted(missing))
            raise ConfigError(f"Level {index} is missing: {keys}")

        for key in self.REQUIRED_KEYS:
            value = level[key]
            if isinstance(value, bool) or not isinstance(value, int):
                raise ConfigError(
                    f"Level {index}: '{key}' must be an integer."
                )

            if key != "seed" and value <= 0:
                raise ConfigError(
                    f"Level {index}: '{key}' must be a positive integer."
                )

        if not 1 <= level["level"] <= 10:
            raise ConfigError(
                f"Level {index}: 'level' must be between 1 and 10."
            )

    def get_level(self, level_number: int) -> dict[str, Any]:
        """Return the configuration for one level."""
        for level in self.levels:
            if level["level"] == level_number:
                return level

        raise ConfigError(f"Level {level_number} does not exist.")


class BaseLevel:
    """Base class containing common level data and behaviour."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.level = config["level"]
        self.width = config["width"]
        self.height = config["height"]
        self.lives = config["lives"]
        self.pacgum = config["pacgum"]
        self.points_per_pacgum = config["points_per_pacgum"]
        self.points_per_super_pacgum = config["points_per_super_pacgum"]
        self.points_per_ghost = config["points_per_ghost"]
        self.seed = config["seed"]
        self.level_max_time = config["level_max_time"]
        self.time_elapsed: float = 0.0

    def update(self, game: Any, delta_time: float) -> None:
        """Update level-specific behaviour."""
        self.time_elapsed += delta_time

    def draw_effects(self, game: Any) -> None:
        """Draw level-specific visual effects (walls)."""
        game.wall_shapes.draw()

    def key_press(self, key):
        return key

    def key_release(self, key, game: Any) -> None:
        return key

    def draw_top_effects(self, game: Any) -> None:
        """Draw effects that must go over ghosts/coins (e.g., Darkness)."""
        pass

    def apply_ghost_speed(self, game: Any, multiplier: float) -> None:
        """Apply a speed multiplier without accumulating it."""
        for ghost in game.ghosts:
            ghost.speed = ghost.og_speed * multiplier


class Level1(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)


class Level2(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.fog_texture = None
        self.light_timer = 0.0
        self.is_dark = False

        self.current_scale = 15.0

    def create_fog_mask(
        self, size: int, vision_radius: int, inner_radius: int
    ):
        bg_r, bg_g, bg_b = 30, 30, 46

        dark_color = (bg_r, bg_g, bg_b, 255)
        img = PIL.Image.new("RGBA", (size, size), dark_color)
        draw = PIL.ImageDraw.Draw(img)
        center = size // 2

        steps = 40
        for i in range(steps, 0, -1):
            r = inner_radius + (vision_radius - inner_radius) * (i / steps)
            alpha = int(255 * (i / steps))
            fill_color = (bg_r, bg_g, bg_b, alpha)
            draw.ellipse([center - r, center - r, center +
                         r, center + r], fill=fill_color)

        draw.ellipse(
            [
                center - inner_radius,
                center - inner_radius,
                center + inner_radius,
                center + inner_radius,
            ],
            fill=(0, 0, 0, 0),
        )
        return arcade.Texture(img)

    def update(self, game: Any, delta_time: float) -> None:
        super().update(game, delta_time)

        self.light_timer += delta_time

        # Lights on and off.
        if self.is_dark:
            if self.light_timer >= 4.0:
                self.is_dark = False
                self.light_timer = 0.0
        else:
            if self.light_timer >= 2.5:
                self.is_dark = True
                self.light_timer = 0.0

        # Resizing the circle.
        target_scale = 1.0 if self.is_dark else 15.0

        animation_speed = 4.0 if self.is_dark else 1.5

        self.current_scale += (
            (target_scale - self.current_scale) * animation_speed * delta_time
        )

        if self.fog_texture is None:
            vision_r = int(game.cell_size * 2.8)
            inner_r = int(game.cell_size * 0.8)
            mask_dim = max(int(game.width * 2.5), 2400)
            self.fog_texture = self.create_fog_mask(
                mask_dim, vision_r, inner_r)

    def draw_top_effects(self, game: Any) -> None:

        # Camera shake.
        if self.fog_texture:
            maze_x = int(game.offset_x - game.shake_x)
            maze_y = int(game.offset_y - game.shake_y)
            maze_w = int(game.cols * game.cell_size)
            maze_h = int(game.rows * game.cell_size)

            game.window.ctx.scissor = (maze_x, maze_y, maze_w, maze_h)

            # Draw the scaled.
            draw_w = self.fog_texture.width * self.current_scale
            draw_h = self.fog_texture.height * self.current_scale

            arcade.draw_texture_rect(
                self.fog_texture,
                arcade.rect.XYWH(
                    game.player.center_x,
                    game.player.center_y,
                    draw_w,
                    draw_h
                )
            )
            game.window.ctx.scissor = None


class Level3(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.revers_time = 0.0

        self.revers_controls = False

    def update(self, game: Any, delta_time: float) -> None:
        super().update(game, delta_time)

        self.revers_time += delta_time

        if self.revers_controls:
            if self.revers_time >= 5.0:
                self.revers_controls = False
                self.revers_time = 0.0
        else:
            if self.revers_time >= 2.0:
                self.revers_controls = True
                self.revers_time = 0.0

    def key_press(self, key: int) -> int:
        """Invert the movement controls when active."""
        if key == arcade.key.UP or key == arcade.key.W:
            return arcade.key.DOWN if self.revers_controls else key
        elif key == arcade.key.DOWN or key == arcade.key.S:
            return arcade.key.UP if self.revers_controls else key
        elif key == arcade.key.LEFT or key == arcade.key.A:
            return arcade.key.RIGHT if self.revers_controls else key
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            return arcade.key.LEFT if self.revers_controls else key

        return key

    def draw_top_effects(self, game: Any) -> None:
        """Draw a flashing warning text for inverted controls."""

        if self.revers_controls:
            if int(self.revers_time * 10) % 2 == 0:
                arcade.draw_text(
                    "CONTROLS INVERTED!",
                    game.width * 0.59,
                    game.height * 0.8,
                    arcade.color.RED,
                    font_size=24.0,
                    font_name="Handjet",
                    bold=True,
                    anchor_x="center",
                    anchor_y="center",
                )


class Level4(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.spin_timer = 0.0
        self.current_angle = 0

    def update(self, game: Any, delta_time: float) -> None:
        super().update(game, delta_time)

        self.spin_timer += delta_time

        if self.spin_timer >= 4.0:
            self.current_angle += 90
            self.spin_timer = 0.0

        if self.current_angle >= 360:
            self.current_angle = 0
            self.spin_timer = 0.0

    def key_press(self, key: int) -> int:
        """Rotate the controls to match the visual screen rotation."""

        if self.current_angle == 0:
            return key

        # Get the right key based on the current angle.
        keys = [arcade.key.UP, arcade.key.RIGHT,
                arcade.key.DOWN, arcade.key.LEFT]
        alt_keys = [arcade.key.W, arcade.key.D, arcade.key.S, arcade.key.A]

        shift = self.current_angle // 90

        if key in keys:
            idx = keys.index(key)
            return keys[(idx + shift) % 4]

        elif key in alt_keys:
            idx = alt_keys.index(key)
            return keys[(idx + shift) % 4]

        return key

    def draw_top_effects(self, game: Any) -> None:
        """Flash a warning right before the screen spins."""
        time_left = 4.0 - self.spin_timer

        # Warn user 1 second before spin.
        if time_left < 1.0:
            if int(time_left * 10) % 2 == 0:
                arcade.draw_text(
                    "SHIFTING!",
                    game.width * 0.59,
                    game.height * 0.8,
                    arcade.color.YELLOW,
                    font_size=30,
                    font_name="Handjet",
                    bold=True,
                    anchor_x="center",
                    anchor_y="center",
                )


class Level5(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.input_text = ""
        self.flash_time = 0.0

    def update(self, game: Any, delta_time: float) -> None:
        super().update(game, delta_time)

        self.flash_time += delta_time

        if self.flash_time >= 1.0:
            self.flash_time = 0.0

    def key_press(self, key: int, game: Any) -> None:

        if game.player.is_dying:
            return

        # Return the direction based on the typed command.
        if key == arcade.key.ENTER or key == arcade.key.RETURN:
            cmd = self.input_text.strip().lower()

            if cmd == "up" or cmd == "UP":
                game.player.queue_direction((0, 1))
            elif cmd == "down" or cmd == "DOWN":
                game.player.queue_direction((0, -1))
            elif cmd == "left" or cmd == "LEFT":
                game.player.queue_direction((-1, 0))
            elif cmd == "right" or cmd == "RIGHT":
                game.player.queue_direction((1, 0))

            # Reset input box.
            self.input_text = ""

        # Delete the last character.
        elif key == arcade.key.BACKSPACE:
            self.input_text = self.input_text[:-1]

    def on_text(self, text: str) -> None:
        """Collect letters typed by the user."""
        if text.isalpha() and len(self.input_text) < 10:
            if text.lower() in ('e', 'q') and self.input_text == "":
                return
            self.input_text += text

    def draw_top_effects(self, game: Any) -> None:
        """Draw the active typing prompt at the top of the UI."""
        end = "_" if self.flash_time < 0.5 else ""
        display_str = f"Type to move: {self.input_text.upper()}{end}"

        arcade.draw_text(
            display_str,
            game.width * 0.59,
            game.height * 0.8,
            arcade.color.CYAN,
            font_size=20.0,
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )


class Level6(BaseLevel):
    """Tracks player grid positions and rubberbands him back to a previous cell
    when moving.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize timing parameters and position anchor trackers."""
        super().__init__(config)
        self.normal_duration: float = 5.0
        self.lag_duration: float = 1.0
        self.cycle_length: float = self.normal_duration + self.lag_duration

        self.timer: float = 0.0
        self.is_lagging: bool = False

        # saved coords.
        self.lag_anchor_x: float = 0.0
        self.lag_anchor_y: float = 0.0

    def update(self, game: Any, delta_time: float) -> None:
        """Update cycle timers and continuously pull Pac-Man back to the anchor
        cell during lag spikes.
        """
        self.timer += delta_time
        current_cycle_time = self.timer % self.cycle_length

        # Check if inside the 1.5-second lag window.
        if current_cycle_time >= self.normal_duration:
            if not self.is_lagging:
                self.is_lagging = True
                # Lock in Pac-Man's exact cell location the instant lag starts.
                self.lag_anchor_x = game.player.center_x
                self.lag_anchor_y = game.player.center_y

            # get the distance between Pac-Man's current position and the
            # anchor position.
            dist_from_anchor = math.hypot(
                game.player.center_x - self.lag_anchor_x,
                game.player.center_y - self.lag_anchor_y,
            )

            # Teleport pacman back.
            if dist_from_anchor > 15.0:
                game.player.center_x = self.lag_anchor_x
                game.player.center_y = self.lag_anchor_y

        else:
            # Return to normal.
            self.is_lagging = False

    def draw_top_effects(self, game: Any) -> None:
        """Render high ping / rubberband warning overlay on screen."""
        current_cycle_time = self.timer % self.cycle_length

        if self.is_lagging:
            arcade.draw_text(
                "! CONNECTION LOST: RUBBERBANDING... !",
                game.width * 0.59,
                game.height * 0.8,
                arcade.color.RED,
                font_size=20,
                font_name="Handjet",
                anchor_x="center",
                bold=True,
            )
        else:
            time_left = max(0.0, self.normal_duration - current_cycle_time)
            arcade.draw_text(
                f"PING: 28ms (LAG SPIKE IN {time_left:.1f}s)",
                game.width * 0.59,
                game.height * 0.8,
                arcade.color.GREEN,
                font_size=18,
                font_name="Handjet",
                anchor_x="center",
                bold=True,
            )


class Level7(BaseLevel):
    """Red light Green light."""

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.timer: float = 0.0
        self.state: str = "GREEN"
        self.is_braking: bool = False

        # Cycle durations in seconds.
        self.green_duration: float = 5.0
        self.yellow_duration: float = 0.75
        self.red_duration: float = 1.0
        self.cycle_length: float = self.green_duration + \
            self.yellow_duration + self.red_duration

    def key_press(self, key: int, game: Any = None) -> int:

        if key == arcade.key.SPACE:
            self.is_braking = True
        return key

    def key_release(self, key: int, game: Any = None) -> None:

        if key == arcade.key.SPACE:
            self.is_braking = False

    def update(self, game: Any, delta_time: float) -> None:

        self.timer += delta_time
        cycle_time = self.timer % self.cycle_length

        # Update the light.
        if cycle_time < self.green_duration:
            self.state = "GREEN"
        elif cycle_time < self.green_duration + self.yellow_duration:
            self.state = "YELLOW"
        else:
            self.state = "RED"

        # Brake pacman if braking.
        if self.is_braking:
            game.player.speed = 0.0
        else:
            multiplier = (game.combo_count // 10) + 1
            bonus = 1.0 + min(0.4, (multiplier - 1) * 0.1)
            game.player.speed = game.player_speed * bonus

        # hit pacman if still moving in red light.
        if (
            self.state == "RED"
            and not self.is_braking
            and game.player.current_dir != (0, 0)
            or game.player.is_powered_up
        ):
            game.handle_player_hit()

    def draw_top_effects(self, game: Any) -> None:

        center_x = game.width * 0.59
        center_y = game.height * 0.8

        # draw red light green light.
        if self.state == "GREEN":
            arcade.draw_text(
                "GREEN LIGHT!",
                center_x, center_y,
                arcade.color.LIME_GREEN, 20, anchor_x="center", bold=True
            )
        elif self.state == "YELLOW":
            arcade.draw_text(
                "YELLOW: BRAKE (SPACE)!",
                center_x, center_y,
                arcade.color.YELLOW, 18, anchor_x="center", bold=True
            )
        elif self.state == "RED":
            arcade.draw_text(
                "RED LIGHT!",
                center_x, center_y,
                arcade.color.RED, 20, anchor_x="center", bold=True
            )


class Level8(BaseLevel):
    """Simon says."""

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.state: str = "NORMAL"  # NORMAL, WAITING, FROZEN
        self.timer: float = 0.0

        self.next_event_time: float = random.uniform(6.0, 10.0)
        self.reaction_time_limit: float = 3
        self.freeze_duration: float = 2.0

        self.current_prompt_text: str = ""
        self.accepted_keys: list[int] = []
        self.is_simon: bool = True

        # Define the base directions
        self.commands = [
            ("UP", [arcade.key.UP, arcade.key.W]),
            ("DOWN", [arcade.key.DOWN, arcade.key.S]),
            ("LEFT", [arcade.key.LEFT, arcade.key.A]),
            ("RIGHT", [arcade.key.RIGHT, arcade.key.D]),
        ]

    def update(self, game: Any, delta_time: float) -> None:
        """Manage the event cycles and freeze penalties."""
        if self.state == "NORMAL":
            self.timer += delta_time
            if self.timer >= self.next_event_time:
                self.trigger_simon_says()

        elif self.state == "WAITING":
            self.timer -= delta_time

            # time!
            if self.timer <= 0:
                # simon said.
                if self.is_simon:
                    self.trigger_freeze()
                # simon did not say.
                else:
                    self.state = "NORMAL"
                    self.timer = 0.0
                    self.next_event_time = random.uniform(6.0, 10.0)

        elif self.state == "FROZEN":
            game.player.speed = 0.0
            self.timer -= delta_time

            if self.timer <= 0:
                self.state = "NORMAL"
                self.timer = 0.0
                self.next_event_time = random.uniform(6.0, 10.0)

                # Restore speed with combo.
                multiplier = (game.combo_count // 10) + 1
                bonus = 1.0 + min(0.4, (multiplier - 1) * 0.1)
                game.player.speed = game.player_speed * bonus

    def trigger_simon_says(self) -> None:
        """Start a random Real or Fake event."""
        self.state = "WAITING"
        self.timer = self.reaction_time_limit

        direction_text, keys = random.choice(self.commands)
        self.accepted_keys = keys

        # schoose simon says or not.
        self.is_simon = random.choice([True, False, True])

        if self.is_simon:
            self.current_prompt_text = (
                f"SIMON SAYS: PRESS {direction_text}...!"
            )
        else:
            self.current_prompt_text = f"PRESS {direction_text}..!"

    def trigger_freeze(self) -> None:
        """Punish the player by freezing them."""
        self.state = "FROZEN"
        self.timer = self.freeze_duration
        self.current_prompt_text = "SYSTEM LOCKED..!"

    def key_press(self, key: int, game: Any = None) -> int | None:
        """Intercept key presses during the event."""

        if self.state == "WAITING":
            if self.is_simon:
                # Simon says.
                if key in self.accepted_keys:
                    # SUCCESS: Right key pressed.
                    self.state = "NORMAL"
                    self.timer = 0.0
                    self.next_event_time = random.uniform(6.0, 10.0)
                    return key
                else:
                    # WRONG KEY: Do not freeze yet, just ignore the input.
                    return None
            else:
                # Simon not says.
                if key in self.accepted_keys:
                    self.trigger_freeze()
                    return None
                else:
                    # Pressed a different key. Let them keep playing normally.
                    return key

        if self.state == "FROZEN":
            return None

        return key

    def draw_top_effects(self, game: Any) -> None:
        """Draw the massive UI prompt to the screen."""
        center_x = game.width * 0.59
        center_y = game.height * 0.8

        if self.state == "WAITING":
            if int(self.timer * 10) % 2 == 0:
                arcade.draw_text(
                    self.current_prompt_text,
                    center_x,
                    center_y,
                    arcade.color.RED,
                    25,
                    anchor_x="center",
                    bold=True,
                    font_name="Handjet",
                )
        elif self.state == "FROZEN":
            arcade.draw_text(
                self.current_prompt_text,
                center_x,
                center_y,
                arcade.color.GRAY,
                24,
                anchor_x="center",
                bold=True,
                font_name="Handjet",
            )


class Level9(BaseLevel):
    """Pac-Man must never stop moving, and ghosts get faster upon player
    death.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.stop_timer: float = 0.0
        self.grace_period: float = 1.0

        self.previous_lives: int = -1
        self.ghost_speed_multiplier: float = 1.15

    def update(self, game: Any, delta_time: float) -> None:
        """Check player movement and scale ghost speeds."""
        # Initialize previous_lives on the first update call.
        if self.previous_lives == -1:
            self.previous_lives = game.player.lives

        if game.player.lives < self.previous_lives:
            self.previous_lives = game.player.lives
            self.increase_ghost_speed(game)

        # dont count if pacman is dying or invincible.
        if game.player.is_dying or game.player.invincible:
            self.stop_timer = 0.0
            return

        # is pacman moving.
        if game.player.current_dir == (0, 0) and not game.player.just_started:
            self.stop_timer += delta_time
            if self.stop_timer >= self.grace_period:
                game.handle_player_hit()
                self.stop_timer = 0.0
        else:
            self.stop_timer = 0.0

    def increase_ghost_speed(self, game: Any) -> None:
        """Apply the speed multiplier to all active ghosts."""
        for ghost in (game.blinky, game.pinky, game.inky, game.clyde):
            if hasattr(ghost, 'speed'):
                ghost.speed *= self.ghost_speed_multiplier

    def draw_top_effects(self, game: Any) -> None:
        """Flash a warning if the player is slowing down."""
        if self.stop_timer > 0.1 and int(self.stop_timer * 10) % 2 == 0:
            arcade.draw_text(
                "RAN KED!",
                game.width * 0.59,
                game.height * 0.8,
                arcade.color.RED,
                font_size=28,
                font_name="Handjet",
                bold=True,
                anchor_x="center",
            )


class Level10(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

    def update(self, game: Any, delta_time: float) -> None:
        pass


class LevelFactory:

    def create_level(
        self,
        level_number: int,
        config: dict[str, Any],
    ) -> BaseLevel:
        classes = {
            1: Level1, 2: Level2, 3: Level3, 4: Level4, 5: Level5,
            6: Level6, 7: Level7, 8: Level8, 9: Level9, 10: Level10
        }
        return classes.get(level_number, Level1)(config)
