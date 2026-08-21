import json
import math
import random
from pathlib import Path
from typing import Any

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
        """Draw level-specific visual effects."""
        game.wall_shapes.draw()

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

    # def draw_effects(self, game: Any) -> None:
    #     game.wall_shapes.draw()


class Level2(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)


    def update(self, game: Any, delta_time: float) -> None:
        """Accumulates elapsed time for animations and state updates."""
        super().update(game, delta_time)


    # def draw_effects(self, game: Any) -> None:

    #     if not game.walls_hidden:
    #         game.wall_shapes.draw()
        

class Level3(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)


class Level4(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

    # def draw_effects(self, game: Any) -> None:
    #     pass


class Level5(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)


    # def draw_effects(self, game: Any) -> None:
    #     pass


class Level6(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

    # def draw_effects(self, game: Any) -> None:
    #     pass


class Level7(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

    # def draw_effects(self, game: Any) -> None:
    #     pass


class Level8(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

    def update(self, game: Any, delta_time: float) -> None:
        pass

    # def draw_effects(self, game: Any) -> None:
    #     pass

class Level9(BaseLevel):

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

    def update(self, game: Any, delta_time: float) -> None:
        pass

    # def draw_effects(self, game: Any) -> None:
    #     pass


class Level10(BaseLevel):
    
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

    def update(self, game: Any, delta_time: float) -> None:
        pass

    # def draw_effects(self, game: Any) -> None:
    #     pass


class LevelFactory:

    def create_level(
        self,
        level_number: int,
        config: dict[str, Any],
    ) -> BaseLevel:
        if level_number == 1:
            return Level1(config)
        if level_number == 2:
            return Level2(config)
        if level_number == 3:
            return Level3(config)
        if level_number == 4:
            return Level4(config)
        if level_number == 5:
            return Level5(config)
        if level_number == 6:
            return Level6(config)
        if level_number == 7:
            return Level7(config)
        if level_number == 8:
            return Level8(config)
        if level_number == 9:
            return Level9(config)
        if level_number == 10:
            return Level10(config)
