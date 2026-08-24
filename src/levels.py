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

        if not isinstance(self.highscore_filename, str) or not self.highscore_filename:
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

    def draw_top_effects(self, game: Any) -> None:
        """Draw effects that must go over ghosts/coins (e.g., Darkness)."""
        pass

    def handle_key(self, key: int) -> int:
        """Allow a level to modify player input."""
        return key

    def apply_ghost_speed(self, game: Any, multiplier: float) -> None:
        """Apply a speed multiplier without accumulating it."""
        for ghost in game.ghosts:
            ghost.speed = ghost.og_speed * multiplier

    def draw_message(self, game: Any, text: str) -> None:
        """Draw a temporary level message."""
        arcade.draw_text(
            text,
            game.width / 2,
            game.height * 0.92,
            arcade.color.WHITE,
            font_size=28,
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )


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

    def create_fog_mask(self, size: int, vision_radius: int, inner_radius: int):
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
            draw.ellipse([center - r, center - r, center + r, center + r], fill=fill_color)

        draw.ellipse([center - inner_radius, center - inner_radius, center + inner_radius, center + inner_radius], fill=(0, 0, 0, 0))
        return arcade.Texture(img)

    def update(self, game: Any, delta_time: float) -> None:
        super().update(game, delta_time)

        self.light_timer += delta_time
        
        #Lights on and off.
        if self.is_dark:
            if self.light_timer >= 4.0:
                self.is_dark = False
                self.light_timer = 0.0
        else:
            if self.light_timer >= 2.5:
                self.is_dark = True
                self.light_timer = 0.0
        
        #Resizing the circle.
        target_scale = 1.0 if self.is_dark else 15.0

        animation_speed = 4.0 if self.is_dark else 1.5

        self.current_scale += (target_scale - self.current_scale) * animation_speed * delta_time

        if self.fog_texture is None:
            vision_r = int(game.cell_size * 2.8)
            inner_r = int(game.cell_size * 0.8)
            mask_dim = max(int(game.width * 2.5), 2400)
            self.fog_texture = self.create_fog_mask(mask_dim, vision_r, inner_r)

    def draw_top_effects(self, game: Any) -> None:
        
        #Camera shake.
        if self.fog_texture:
            maze_x = int(game.offset_x - game.shake_x)
            maze_y = int(game.offset_y - game.shake_y)
            maze_w = int(game.cols * game.cell_size)
            maze_h = int(game.rows * game.cell_size)

            game.window.ctx.scissor = (maze_x, maze_y, maze_w, maze_h)

            #Draw the scaled.
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


class Level4(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)


class Level5(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)


class Level6(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)


class Level7(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)


class Level8(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

    def update(self, game: Any, delta_time: float) -> None:
        pass


class Level9(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

    def update(self, game: Any, delta_time: float) -> None:
        pass


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

