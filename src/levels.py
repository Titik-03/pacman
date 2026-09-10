import json
import math
import random
from pathlib import Path
from typing import Any
import PIL.Image
import PIL.ImageDraw

import arcade


import re
import sys


class ConfigError(Exception):
    """Raised when the game configuration is invalid."""


class ConfigParser:
    """Loads and validates the JSON game configuration."""

    DEFAULTS: dict[str, Any] = {
        "lives": 3,
        "pacgum": 42,
        "points_per_pacgum": 10,
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,
        "seed": 42,
        "level_max_time": 90,
        "width": 15,
        "height": 15,
    }

    def __init__(self, filename: str = "src/jsons/config.json") -> None:
        """Initialize ConfigParser with config path and load settings."""
        self.filename = Path(filename)
        self.levels: list[dict[str, Any]] = []
        self.highscore_filename = "src/outputs/high_score.json"
        self.load()

    def load(self) -> None:
        """Read, parse and validate the configuration."""
        if not self.filename.exists():
            print(
                f"Warning: Config file {self.filename} not found. "
                "Using defaults.",
                file=sys.stderr,
            )
            data: dict[str, Any] = {}
        else:
            content = self.read_file()
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                print(
                    f"Warning: Failed to parse JSON config: {e}. "
                    "Using defaults.",
                    file=sys.stderr,
                )
                data = {}

        if not isinstance(data, dict):
            print(
                "Warning: Config root must be object. Using defaults.",
                file=sys.stderr,
            )
            data = {}

        self.highscore_filename = str(
            data.get("highscore_filename", "src/outputs/high_score.json")
        )

        raw_levels = data.get("levels", [])
        if not isinstance(raw_levels, list):
            print(
                "Warning: 'levels' key must be a list. Using default levels.",
                file=sys.stderr,
            )
            raw_levels = []

        parsed_levels: list[dict[str, Any]] = []
        if raw_levels:
            for index, lvl in enumerate(raw_levels, start=1):
                lvl_dict = lvl if isinstance(lvl, dict) else {}
                lvl_num = lvl_dict.get("level", index)
                if not isinstance(lvl_num, int):
                    lvl_num = index
                parsed_levels.append(self.sanitize_level(lvl_dict, lvl_num))
        else:
            for index in range(1, 11):
                parsed_levels.append(self.sanitize_level({}, index))

        self.levels = parsed_levels
        self.max_level = max(1, len(self.levels))

    def read_file(self) -> str:
        """Read file and ignore lines/inline text beginning with # or //."""
        lines = []

        try:
            with self.filename.open("r", encoding="utf-8") as file:
                for line in file:
                    # Strip single-line or inline comments
                    cleaned = re.sub(r"(#|//).*", "", line)
                    lines.append(cleaned)
        except OSError:
            print(f"Warning: Cannot read {self.filename}", file=sys.stderr)
            return "{}"

        return "".join(lines)

    def sanitize_level(
        self, level: dict[str, Any], index: int
    ) -> dict[str, Any]:
        """Sanitize one level config with clamping to safe defaults."""
        result: dict[str, Any] = {"level": index}

        for key, default_val in self.DEFAULTS.items():
            val = level.get(key)
            if not isinstance(val, int) or isinstance(val, bool):
                if val is not None:
                    print(
                        f"Warning: Level {index} key '{key}' invalid ({val}). "
                        f"Clamping to default {default_val}.",
                        file=sys.stderr,
                    )
                result[key] = default_val
            elif key != "seed" and val <= 0:
                print(
                    f"Warning: Level {index} key '{key}' must be positive "
                    f"({val}). Clamping to default {default_val}.",
                    file=sys.stderr,
                )
                result[key] = default_val
            else:
                result[key] = val

        return result

    def get_level(self, level_number: int) -> dict[str, Any]:
        """Return the configuration for one level."""
        for level in self.levels:
            if level["level"] == level_number:
                return level

        return self.sanitize_level({}, level_number)


class BaseLevel:
    """Base class containing common level data and behaviour."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize base level settings, timing, and point thresholds."""
        self.level = config["level"]
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

    def key_press(self, key: int, *args: Any, **kwargs: Any) -> Any:
        """Handle level-specific key press modifications."""
        return key

    def key_release(self, key: int, game: Any) -> Any:
        """Handle level-specific key release modifications."""
        return key

    def draw_top_effects(self, game: Any) -> None:
        """Draw effects that must go over ghosts/coins (e.g., Darkness)."""
        pass

    def apply_ghost_speed(self, game: Any, multiplier: float) -> None:
        """Apply a speed multiplier without accumulating it."""
        for ghost in game.ghosts:
            ghost.speed = ghost.og_speed * multiplier


class Level1(BaseLevel):
    """Level 1: standard Pac-Man gameplay without modifiers."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize Level 1 configuration."""
        super().__init__(config)


class Level2(BaseLevel):
    """Level 2: darkness mechanic with dynamic flashlight mask."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize Level 2 darkness state and timers."""
        super().__init__(config)
        self.fog_texture = None
        self.light_timer = 0.0
        self.is_dark = False

        self.current_scale = 15.0

    def create_fog_mask(
        self, size: int, vision_radius: int, inner_radius: int
    ) -> Any:
        """Generate a circular transparent flashlight mask texture."""
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
        """Toggle darkness cycle and scale the vision mask."""
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
        """Render the dark fog mask over the maze."""

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
    """Level 3: periodic inverted movement controls."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize inverted controls state and timers."""
        super().__init__(config)
        self.revers_time = 0.0

        self.revers_controls = False

    def update(self, game: Any, delta_time: float) -> None:
        """Toggle inverted control state on fixed intervals."""
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
                    game.width * 0.255,
                    game.height * 0.961,
                    arcade.color.RED,
                    font_size=24.0,
                    font_name="Handjet",
                    bold=True,
                    anchor_x="center",
                    anchor_y="center",
                )


class Level4(BaseLevel):
    """Level 4: periodic maze rotation and shifted directional inputs."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize rotation angle and interval timers."""
        super().__init__(config)
        self.spin_timer = 0.0
        self.current_angle = 0

    def update(self, game: Any, delta_time: float) -> None:
        """Advance timer and increment camera angle by 90 degrees."""
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
        keys: list[int] = [arcade.key.UP, arcade.key.RIGHT,
                           arcade.key.DOWN, arcade.key.LEFT]
        alt_keys: list[int] = [arcade.key.W, arcade.key.D,
                               arcade.key.S, arcade.key.A]

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
                    game.width * 0.255,
                    game.height * 0.961,
                    arcade.color.YELLOW,
                    font_size=30,
                    font_name="Handjet",
                    bold=True,
                    anchor_x="center",
                    anchor_y="center",
                )


class Level5(BaseLevel):
    """Level 5: text-based command movement control."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize text input buffer and cursor timer."""
        super().__init__(config)
        self.input_text = ""
        self.flash_time = 0.0

    def update(self, game: Any, delta_time: float) -> None:
        """Update typing cursor blink timer."""
        super().update(game, delta_time)

        self.flash_time += delta_time

        if self.flash_time >= 1.0:
            self.flash_time = 0.0

    def key_press(self, key: int, game: Any) -> None:
        """Process typed words on Enter or delete with Backspace."""

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
                game.width * 0.255,
                game.height * 0.961,
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
                game.width * 0.255,
                game.height * 0.961,
                arcade.color.GREEN,
                font_size=18,
                font_name="Handjet",
                anchor_x="center",
                bold=True,
            )


class Level7(BaseLevel):
    """Level 7: Red Light, Green Light stop-and-go mechanic."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize traffic light phases and brake state."""
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
        """Engage brake when spacebar is pressed."""
        if key == arcade.key.SPACE:
            self.is_braking = True
        return key

    def key_release(self, key: int, game: Any = None) -> None:
        """Release brake when spacebar is released."""
        if key == arcade.key.SPACE:
            self.is_braking = False

    def update(self, game: Any, delta_time: float) -> None:
        """Cycle traffic light states and penalize movement on red."""
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
            if hasattr(game, "get_target_player_speed"):
                game.player.speed = game.get_target_player_speed(bonus)
            else:
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
        """Render current traffic light status on the HUD."""
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
    """Lahcen says."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize Simon Says commands and reaction timers."""
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
                if hasattr(game, "get_target_player_speed"):
                    game.player.speed = game.get_target_player_speed(bonus)
                else:
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
                f"LAHCEN SAYS: PRESS {direction_text}...!"
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
        self.ghost_speed_multiplier: float = 1.08

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
                game.width * 0.255,
                game.height * 0.961,
                arcade.color.RED,
                font_size=28,
                font_name="Handjet",
                bold=True,
                anchor_x="center",
            )


class Level10(BaseLevel):
    """Level 10: final challenge level."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize Level 10 configuration."""
        super().__init__(config)

    def update(self, game: Any, delta_time: float) -> None:
        """Update Level 10 gameplay logic."""
        pass


class LevelFactory:
    """Factory to instantiate level instances from level numbers."""

    def create_level(
        self,
        level_number: int,
        config: dict[str, Any],
    ) -> BaseLevel:
        """Return the level instance corresponding to the given number."""
        classes = {
            1: Level1, 2: Level2, 3: Level3, 4: Level4, 5: Level5,
            6: Level6, 7: Level7, 8: Level8, 9: Level9, 10: Level10
        }
        return classes.get(level_number, Level1)(config)
