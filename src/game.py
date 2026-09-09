from typing import Any
from arcade import load_texture
import random
import math
import pathlib
import arcade
import arcade.shape_list as shapes
from mazegenerator import MazeGenerator
from src.coins import Coin
from src.player import Player
# from src.pause_menu import PauseMenu
from src.game_over import GameOver
from src.vectory import Vectory
from src.ghost import Blinky, Pinky, Inky, Clyde
from src.cheat_menu import CheatMenu
from src.particle import (
    ShatterParticle,
    Floating_score,
    TrailParticle,
    Shockwave,
    CoinSparkle,
)
from src.levels import ConfigParser, LevelFactory
from src.sound_manager import SoundManager


SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
BLINKY_PATH = SCRIPT_DIR / "assets" / "blinky.png"
PINKY_PATH = SCRIPT_DIR / "assets" / "pinky.png"
# INKY_PATH = SCRIPT_DIR / "assets" / "ghost.png"
# CLYDE_PATH = SCRIPT_DIR / "assets" / "ghost.png"

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

# Catppuccin Mocha Palette
MOCHA_BASE = (30, 30, 46)        # #1e1e2e
MOCHA_TEXT = (205, 214, 244)     # #cdd6f4
MOCHA_MAUVE = (203, 166, 247)    # #cba6f7
MOCHA_LAVENDER = (180, 190, 254)  # b4befe
MOCHA_CRUST = (17, 17, 27)       # #11111b
MOCHA_RED = (243, 139, 168)      # #f38ba8
MOCHA_GREEN = (166, 227, 161)    # #a6e3a1
MOCHA_SURFACE0 = (49, 50, 68)    # #313244
MOCHA_SURFACE1 = (69, 71, 90)    # #45475a
MOCHA_MANTLE = (24, 24, 37)      # #181825

NEON = (203, 166, 247, 255)
GLOW = (203, 166, 247, 80)


class GameWindow(arcade.View):
    """Main game view that manages gameplay, rendering, and input."""

    def __init__(self,
                 menu: arcade.View,
                 window: arcade.Window,
                 seed: int = 42,
                 level: int = 1,
                 score: int = 0,
                 lives: int | None = None,
                 ) -> None:
        """Initialize the game state, maze, player, ghosts, and UI."""

        super().__init__()
        self.main_menu = menu
        self.config_parser = getattr(
            self.main_menu, "config_parser", None
        ) or ConfigParser()
        self.level_factory = LevelFactory()
        self.level = level
        self.score = score
        # self.seed = seed
        self.walls_hidden = False

        # try:
        level_config = self.config_parser.get_level(self.level)
        # except Exception:
        #     level_config = self.config_parser.get_level(1)

        self.level_obj = self.level_factory.create_level(
            self.level, level_config)

        try:
            maze_w = getattr(self.level_obj, "width", 15)
            maze_h = getattr(self.level_obj, "height", 15)
            self.m = MazeGenerator(
                (maze_h, maze_w), perfect=False, seed=self.level_obj.seed
            )
            self.maze = self.m.maze
        except Exception as e:
            import sys
            print(
                f"Warning: MazeGenerator failed ({e}). Using default grid.",
                file=sys.stderr,
            )
            self.maze = [[0 for _ in range(15)] for _ in range(15)]

        self.rows = len(self.maze)
        self.cols = len(self.maze[0])
        self.background = load_texture("src/assets/Dek.png")
        self.abilities = [load_texture("src/assets/1.png"),
                          load_texture("src/assets/4.png"),
                          load_texture("src/assets/6.png"),
                          load_texture("src/assets/8.png"),]

        # Position maze within the dark left area of Dek.png
        left_area_width = self.width * 0.52
        margin_x = 80
        margin_y = 100
        available_w = left_area_width - margin_x
        available_h = self.height - margin_y
        self.cell_size = min(available_w // self.cols,
                             available_h // self.rows)

        self.offset_x = (left_area_width - self.cols * self.cell_size) / 2
        self.offset_y = (self.height - self.rows * self.cell_size) / 2

        self.coin = Coin(10, 10)
        self.target_coins = 0
        self.collected_coins = 0

        # Load Handjet font
        font_path = (
            SCRIPT_DIR / "assets" / "Handjet" / "static" / "Handjet-Bold.ttf"
        )
        if font_path.exists():
            arcade.load_font(str(font_path))

        # Text UI objects positioned next to labels in Dek.png
        font_sz = int(32 * (self.height / 1080.0))
        self.score_text = arcade.Text(
            text=f"{self.score}",
            x=self.width * 0.77,
            y=self.height * 0.97,
            color=MOCHA_CRUST,
            font_size=font_sz,
            font_name="Handjet",
            bold=True,
            anchor_y="center"
        )

        self.lives_x = self.width * 0.81
        self.lives_y = self.height * 0.875

        self.level_text = arcade.Text(
            text=f"{self.level}",
            x=self.width * 0.84,
            y=self.height * 0.784,
            color=MOCHA_CRUST,
            font_size=font_sz,
            font_name="Handjet",
            bold=True,
            anchor_y="center"
        )

        self.timer = float(self.level_obj.level_max_time)

        self.time_text = arcade.Text(
            text=f"{int(self.timer)}s",
            x=self.width * 0.87,
            y=self.height * 0.698,
            color=MOCHA_CRUST,
            font_size=font_sz,
            font_name="Handjet",
            bold=True,
            anchor_y="center"
        )

        # player coords.
        center_col = self.cols // 2
        center_row = self.rows // 2
        start_x = self.offset_x + (center_col + 0.5) * self.cell_size
        start_y = self.offset_y + \
            (self.rows - 1 - center_row + 0.5) * self.cell_size

        self.player, self.player_list = Player.create_player(
            start_x, start_y, self.cell_size)
        if lives is not None:
            self.player.lives = lives
        else:
            self.player.lives = self.level_obj.lives

        self.player_spawn_x = start_x
        self.player_spawn_y = start_y

        self.player_speed = 180
        self.speed_up = False

        self.init_ghosts()

        self.wall_shapes: shapes.ShapeElementList = shapes.ShapeElementList()
        self.wall_list: arcade.SpriteList = arcade.SpriteList(
            use_spatial_hash=True
        )
        self.coins_lst: list[Coin] = []

        self.init_maze()

        self.target_score = len(self.coins_lst) + 196

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.wall_list)

        self.manager = arcade.gui.UIManager()

        self.main_menu = menu
        self.config_parser = getattr(
            self.main_menu, "config_parser", None
        ) or ConfigParser()
        # self.pause_menu = PauseMenu(self)
        self.cheat_menu: Any = CheatMenu(self)
        self.pause = False
        self.cheat_menu = False
        self.cheat_menu_timer = 0.0

        self.debug = False
        self.freeze_ghosts = False

        self.game_over: GameOver | None = None
        self.vectory: Vectory | None = None
        self.shatter_particles: list[ShatterParticle] = []
        self.camera = arcade.Camera2D()
        self.ui_camera = arcade.Camera2D()
        self.spin_camera = arcade.Camera2D()
        self.floating_scores: list[Floating_score] = []

        self.shake_time = 0.0
        self.shake_intensity = 0.0
        self.shake_x = 0.0
        self.shake_y = 0.0
        self.is_hit = False
        self.power_time = 10
        self.power_left = 10

        self.combo_count = 0
        self.combo_timer = 0.0
        self.combo_limit = 1.5

        self.mouse_x = 0.0
        self.mouse_y = 0.0

        # Ability system
        self.ability_defs: list[dict[str, Any]] = [
            {
                "name": "FROST WALK [E]",
                "key": arcade.key.E,
                "unlock_level": 3,
                "duration": 5.0,
                "cooldown": 20.0,
                "active_timer": 0.0,
                "cooldown_timer": 0.0,
                "icon_index": 1,
                "effect": "frost_walk",
            },
            {
                "name": "STOP TIME [Q]",
                "key": arcade.key.Q,
                "unlock_level": 5,
                "duration": 5.0,
                "cooldown": 20.0,
                "active_timer": 0.0,
                "cooldown_timer": 0.0,
                "icon_index": 2,
                "effect": "stop_time",
            },
            {
                "name": "TELEPORT [F]",
                "key": arcade.key.F,
                "unlock_level": 7,
                "duration": 0.0,
                "cooldown": 20.0,
                "active_timer": 0.0,
                "cooldown_timer": 0.0,
                "icon_index": 3,
                "effect": "teleport",
            },
        ]
        # --- Motion Trail State ---
        self.trail_particles: list[TrailParticle] = []
        self.trail_timer = 0.0
        self.TRAIL_INTERVAL = 0.04
        self.shock: list[Shockwave] = []
        self.coin_sparkles: list[CoinSparkle] = []

    def get_unlocked_abilities(self) -> list[dict[str, Any]]:
        """Return the list of abilities unlocked at the current level."""
        return [
            ability for ability in self.ability_defs
            if self.level >= ability["unlock_level"]
        ]

    def get_ability_by_key(self, key: int) -> dict[str, Any] | None:
        """Return the ability bound to the given key, or None if locked."""
        for ability in self.ability_defs:
            if key == ability["key"] and self.level >= ability["unlock_level"]:
                return ability
        return None

    def get_player_facing_dir(self) -> tuple[int, int]:
        """Return the direction the player is currently facing."""
        if self.player.current_dir != (0, 0):
            return self.player.current_dir
        if self.player.queued_dir != (0, 0):
            return self.player.queued_dir
        return (0, 0)

    def get_furthest_tile_in_direction(
        self,
        start_row: int,
        start_col: int,
        direction: tuple[int, int],
    ) -> tuple[int, int]:
        """Find the furthest open tile in a direction before a wall."""
        dx, dy = direction
        row, col = start_row, start_col

        while True:
            next_row = row - dy
            next_col = col + dx

            if not (0 <= next_row < self.rows and 0 <= next_col < self.cols):
                break

            cell_val = self.maze[row][col]

            if dy == 1 and (cell_val & NORTH):
                break
            if dy == -1 and (cell_val & SOUTH):
                break
            if dx == 1 and (cell_val & EAST):
                break
            if dx == -1 and (cell_val & WEST):
                break

            row, col = next_row, next_col

        return row, col

    def reset_ghost_colors(self) -> None:
        """Update ghost tint colors based on current game state."""
        active_stop_time = self.get_ability_by_key(arcade.key.Q)
        active_frost_walk = self.get_ability_by_key(arcade.key.E)

        for ghost in (self.blinky, self.pinky, self.inky, self.clyde):
            if ghost.state == "EATEN":
                continue

            if self.player.is_powered_up and ghost.state == "FRIGHTENED":
                if self.player.power_timer <= 3.0:
                    is_white = int(self.player.power_timer * 6.5) % 2 == 0
                    ghost.color = (
                        (255, 255, 255) if is_white else (137, 180, 250)
                    )
                else:
                    ghost.color = (255, 255, 255)
                continue

            if ghost.state == "FRIGHTENED" and not self.player.is_powered_up:
                ghost.state = "CHASE"
                ghost.texture = arcade.load_texture(ghost.normal_texture_path)
                ghost.was_eaten = False

            if (
                active_stop_time is not None
                and active_stop_time["active_timer"] > 0
                and ghost.state == "CHASE"
            ):
                ghost.color = (130, 200, 255)
            elif (
                active_frost_walk is not None
                and active_frost_walk["active_timer"] > 0
                and ghost.state == "CHASE"
            ):
                ghost.color = (140, 210, 255)
            else:
                ghost.color = (255, 255, 255)

    def trigger_shake(self, duration: float, intensity: float) -> None:
        """Start screen shake effect with given duration and intensity."""
        self.shake_time = duration
        self.shake_intensity = intensity

    def on_mouse_motion(
        self, x: float, y: float, dx: float, dy: float
    ) -> None:
        """Track the current mouse position."""
        self.mouse_x = x
        self.mouse_y = y

    def init_ghosts(self) -> None:
        """Create and position all four ghosts in their home corners."""

        # Blinky init.
        blinky_row = 0
        blinky_col = 0

        blinky_x = self.offset_x + (blinky_col + 0.5) * self.cell_size
        blinky_y = self.offset_y + \
            (self.rows - 1 - blinky_row + 0.5) * self.cell_size

        self.blinky, self.blinky_list = Blinky.create_ghost(
            blinky_x,
            blinky_y,
            self.cell_size,
            "blinky"
        )

        self.blinky.home_row, self.blinky.home_col = self.blinky.get_cell(
            self.blinky.center_x,
            self.blinky.center_y,
            self.cell_size,
            self.rows,
            self.offset_x,
            self.offset_y
        )

        # Pinky init.
        pinky_row = 0
        pinky_col = self.cols - 1

        pinky_x = self.offset_x + (pinky_col + 0.5) * self.cell_size
        pinky_y = self.offset_y + \
            (self.rows - 1 - pinky_row + 0.5) * self.cell_size

        self.pinky, self.pinky_list = Pinky.create_ghost(
            pinky_x,
            pinky_y,
            self.cell_size,
            "pinky"
        )

        self.pinky.home_row, self.pinky.home_col = self.pinky.get_cell(
            self.pinky.center_x,
            self.pinky.center_y,
            self.cell_size,
            self.rows,
            self.offset_x,
            self.offset_y
        )

        # Inky init.
        inky_row = self.rows - 1
        inky_col = 0

        inky_x = self.offset_x + (inky_col + 0.5) * self.cell_size
        inky_y = self.offset_y + \
            (self.rows - 1 - inky_row + 0.5) * self.cell_size

        self.inky, self.inky_list = Inky.create_ghost(
            inky_x,
            inky_y,
            self.cell_size,
            "inky"
        )

        self.inky.home_row, self.inky.home_col = self.inky.get_cell(
            self.inky.center_x,
            self.inky.center_y,
            self.cell_size,
            self.rows,
            self.offset_x,
            self.offset_y
        )

        # Clyde init.
        clyde_row = self.rows - 1
        clyde_col = self.cols - 1

        clyde_x = self.offset_x + (clyde_col + 0.5) * self.cell_size
        clyde_y = self.offset_y + \
            (self.rows - 1 - clyde_row + 0.5) * self.cell_size

        self.clyde, self.clyde_list = Clyde.create_ghost(
            clyde_x,
            clyde_y,
            self.cell_size,
            "clyde"
        )

        self.clyde.home_row, self.clyde.home_col = self.clyde.get_cell(
            self.clyde.center_x,
            self.clyde.center_y,
            self.cell_size,
            self.rows,
            self.offset_x,
            self.offset_y
        )

    def init_maze(self) -> None:
        """Build the maze walls, coins, and power pellets from the grid."""

        cs = self.cell_size
        wall_thickness = 4

        corner_cells = {
            (0, 0),
            (0, self.cols - 1),
            (self.rows - 1, 0),
            (self.rows - 1, self.cols - 1)
        }

        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.maze[row][col]
                x = self.offset_x + col * cs
                y = self.offset_y + (self.rows - 1 - row) * cs
                if (row, col) in corner_cells:
                    self.coins_lst.append(
                        Coin(x + cs / 2, y + cs / 2, is_powerup=True))
                elif cell & 0b1111 != 0b1111 and random.choice([True, False]):
                    self.coins_lst.append(
                        Coin(x + cs / 2, y + cs / 2, is_powerup=False))
                elif cell & 0b1111 == 0b1111:
                    self.wall_shapes.append(shapes.create_rectangle(
                        x + cs / 2, y + cs / 2, cs - 3, cs - 3,
                        (*MOCHA_RED, 255)))
                if cell & NORTH:
                    self.wall_shapes.append(shapes.create_line(
                        x, y + cs, x + cs, y + cs, GLOW, 6))
                    self.wall_shapes.append(shapes.create_line(
                        x, y + cs, x + cs, y + cs, NEON, 2))
                    w = arcade.SpriteSolidColor(
                        int(cs), wall_thickness, color=(0, 0, 0, 0))
                    w.center_x = x + cs / 2
                    w.center_y = y + cs
                    self.wall_list.append(w)

                if cell & SOUTH:
                    self.wall_shapes.append(
                        shapes.create_line(x, y, x + cs, y, GLOW, 6))
                    self.wall_shapes.append(
                        shapes.create_line(x, y, x + cs, y, NEON, 2))
                    w = arcade.SpriteSolidColor(
                        int(cs), wall_thickness, color=(0, 0, 0, 0))
                    w.center_x = x + cs / 2
                    w.center_y = y
                    self.wall_list.append(w)

                if cell & EAST:
                    self.wall_shapes.append(shapes.create_line(
                        x + cs, y, x + cs, y + cs, GLOW, 6))
                    self.wall_shapes.append(shapes.create_line(
                        x + cs, y, x + cs, y + cs, NEON, 2))
                    w = arcade.SpriteSolidColor(
                        wall_thickness, int(cs), color=(0, 0, 0, 0))
                    w.center_x = x + cs
                    w.center_y = y + cs / 2
                    self.wall_list.append(w)

                if cell & WEST:
                    self.wall_shapes.append(
                        shapes.create_line(x, y, x, y + cs, GLOW, 6))
                    self.wall_shapes.append(
                        shapes.create_line(x, y, x, y + cs, NEON, 2))
                    w = arcade.SpriteSolidColor(
                        wall_thickness, int(cs), color=(0, 0, 0, 0))
                    w.center_x = x
                    w.center_y = y + cs / 2
                    self.wall_list.append(w)

        self.target_coins = len(self.coins_lst)

    def draw_background_image(self) -> None:
        """Clear the screen and draw the background texture."""
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(
                0,
                0,
                self.width,
                self.height
            )
        )

    def draw_ability(self) -> None:
        """Draw the current ability icon on the HUD."""
        unlocked = self.get_unlocked_abilities()
        idx = unlocked[-1]["icon_index"] if unlocked else 0
        arcade.draw_texture_rect(
            self.abilities[idx],
            arcade.LBWH(1140, 60, 400, 630)
        )

    def draw_cooldown_slider(self) -> None:
        """Draw the ability cooldown progress bar on the HUD."""
        x = 1550
        w = 280
        h = 24
        for row, ability in enumerate(self.get_unlocked_abilities()):
            y = 180 - row * 62
            active_remaining = float(ability["active_timer"])
            cooldown_remaining = float(ability["cooldown_timer"])
            duration = float(ability["duration"])
            cooldown = float(ability["cooldown"])

            if active_remaining > 0:
                status_text = f"ACTIVE {active_remaining:.1f}s"
                accent_color = (137, 220, 255)
                progress = (
                    active_remaining / duration if duration else 0.0
                )
            elif cooldown_remaining > 0:
                status_text = f"{cooldown_remaining:.1f}s"
                accent_color = MOCHA_MAUVE
                progress = (
                    1.0 - (cooldown_remaining / cooldown) if cooldown else 1.0
                )
            else:
                status_text = "READY"
                accent_color = MOCHA_GREEN
                progress = 1.0

            arcade.draw_text(
                ability["name"],
                x=x,
                y=y + h + 14,
                color=MOCHA_TEXT,
                font_size=18,
                font_name="Handjet",
                bold=True,
                anchor_y="center"
            )
            arcade.draw_text(
                status_text,
                x=x + w,
                y=y + h + 14,
                color=accent_color,
                font_size=18,
                font_name="Handjet",
                bold=True,
                anchor_x="right",
                anchor_y="center"
            )
            arcade.draw_rect_filled(
                arcade.LBWH(x - 2, y - 2, w + 4, h + 4),
                color=(17, 17, 27, 200)
            )
            arcade.draw_rect_filled(
                arcade.LBWH(x, y, w, h),
                color=(30, 30, 46, 235)
            )
            for pct in (0.25, 0.5, 0.75):
                tick_x = x + w * pct
                arcade.draw_line(
                    tick_x, y + 3,
                    tick_x, y + h - 3,
                    color=(69, 71, 90, 140),
                    line_width=1
                )
            fill_max_w = w - 6
            fill_w = fill_max_w * max(0.0, min(1.0, progress))
            if fill_w > 0:
                arcade.draw_rect_filled(
                    arcade.LBWH(x + 3, y + 3, fill_w, h - 6),
                    color=accent_color
                )
                arcade.draw_rect_filled(
                    arcade.LBWH(x + 3, y + h / 2, fill_w, (h - 6) / 2),
                    color=(255, 255, 255, 60)
                )

            is_ready = cooldown_remaining <= 0
            border_color = accent_color if is_ready else MOCHA_SURFACE1
            arcade.draw_rect_outline(
                arcade.LBWH(x, y, w, h),
                color=border_color,
                border_width=2
            )

            knob_x = min(x + w - 5, max(x + 5, x + 3 + fill_w))
            knob_cy = y + h / 2
            knob_w = 10
            knob_h = h + 8

            arcade.draw_rect_filled(
                arcade.rect.XYWH(knob_x, knob_cy, knob_w, knob_h),
                color=(245, 245, 255)
            )
            # Knob accent border
            arcade.draw_rect_outline(
                arcade.rect.XYWH(knob_x, knob_cy, knob_w, knob_h),
                color=accent_color,
                border_width=2
            )
            # Center grip notch
            arcade.draw_line(
                knob_x, knob_cy - 4,
                knob_x, knob_cy + 4,
                color=MOCHA_SURFACE0,
                line_width=2
            )

    def trigger_ability(self, key: int) -> None:
        """Activate the ability bound to the given key if it's ready."""
        ability = self.get_ability_by_key(key)
        if ability is None:
            return

        if ability["cooldown_timer"] > 0 or ability["active_timer"] > 0:
            return

        effect = ability["effect"]

        if effect == "frost_walk":
            ability["active_timer"] = ability["duration"]
            ability["cooldown_timer"] = ability["cooldown"]
            SoundManager.get().play_sfx("power_pellet")

        elif effect == "stop_time":
            ability["active_timer"] = ability["duration"]
            ability["cooldown_timer"] = ability["cooldown"]
            SoundManager.get().play_sfx("power_pellet")

        elif effect == "teleport":
            direction = self.get_player_facing_dir()
            if direction == (0, 0):
                return

            ability["cooldown_timer"] = ability["cooldown"]

            col = int(
                round(((self.player.center_x - self.offset_x) -
                      self.cell_size / 2) / self.cell_size)
            )
            row = int(
                round(
                    (
                        (self.rows - 1) * self.cell_size
                        + self.cell_size / 2
                        - (self.player.center_y - self.offset_y)
                    )
                    / self.cell_size
                )
            )
            row, col = self.get_furthest_tile_in_direction(row, col, direction)

            self.player.center_x = self.offset_x + (col + 0.5) * self.cell_size
            self.player.center_y = self.offset_y + (
                self.rows - 1 - row + 0.5
            ) * self.cell_size
            self.player.target_x = self.player.center_x
            self.player.target_y = self.player.center_y
            self.player.current_dir = (0, 0)
            self.player.queued_dir = (0, 0)
            SoundManager.get().play_sfx("power_pellet")

    def draw_maze_background(self) -> None:
        """Draw the dark background and border behind the maze."""
        self.maze_width = self.cols * self.cell_size
        self.maze_height = self.rows * self.cell_size

        arcade.draw_rect_filled(
            arcade.LBWH(
                self.offset_x,       # Left edge of the maze
                self.offset_y,       # Bottom edge of the maze
                self.maze_width,          # Total maze width
                self.maze_height          # Total maze height
            ),
            color=(30, 30, 46, 220))
        arcade.draw_rect_outline(
            arcade.LBWH(
                self.offset_x,
                self.offset_y,
                self.maze_width + 1,
                self.maze_height + 1
            ),
            color=MOCHA_MAUVE,  # Mauve neon border
            border_width=2
        )

    def draw_debug(self) -> None:
        """Draw ghost target markers and grid debug info."""

        self.blinky.draw_target_x(
            self.cell_size,
            self.offset_x,
            self.offset_y,
            rows=self.rows,
            color=arcade.color.RED,
        )
        self.pinky.draw_target_x(
            self.cell_size,
            self.offset_x,
            self.offset_y,
            rows=self.rows,
            color=arcade.color.PINK,
        )
        self.inky.draw_target_x(
            self.cell_size,
            self.offset_x,
            self.offset_y,
            rows=self.rows,
            color=arcade.color.CYAN,
        )
        self.clyde.draw_target_x(
            self.cell_size,
            self.offset_x,
            self.offset_y,
            rows=self.rows,
            color=arcade.color.ORANGE,
        )

        arcade.draw_text(
            f"Mouse coords: {self.mouse_x, self.mouse_y}",
            10, 10
        )

    def draw_hearts(self) -> None:
        """Draw life hearts on the HUD, capped at 5 with a multiplier."""
        # Draw red hearts for lives next to LIVES: label in Dek.png
        size = 14 * (self.height / 1080.0)
        spacing = 38 * (self.width / 1920.0)
        color = MOCHA_RED

        lives = max(0, self.player.lives)
        max_hearts = 5
        hearts_to_draw = min(lives, max_hearts)

        for i in range(hearts_to_draw):
            cx = self.lives_x + i * spacing
            cy = self.lives_y
            arcade.draw_circle_filled(
                cx - size * 0.35, cy + size * 0.15, size * 0.4, color)
            arcade.draw_circle_filled(
                cx + size * 0.35, cy + size * 0.15, size * 0.4, color)
            arcade.draw_triangle_filled(
                cx - size * 0.72, cy + size * 0.15,
                cx + size * 0.72, cy + size * 0.15,
                cx, cy - size * 0.7,
                color
            )

        if lives > max_hearts:
            font_sz = int(24 * (self.height / 1080.0))
            text_x = self.lives_x + max_hearts * spacing - 10
            arcade.draw_text(
                f"x{lives}",
                x=text_x,
                y=self.lives_y + 3,
                color=MOCHA_RED,
                font_size=font_sz,
                font_name="Handjet",
                bold=True,
                anchor_y="center"
            )

    def draw_cheat_menu(self) -> None:
        """Draw the cheat menu overlay with toggle options."""
        # blur.
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                self.width / 2,
                self.height / 2,
                self.width,
                self.height
            ),
            color=(10, 10, 20, 200)
        )

        menu_w, menu_h = 550, 670
        cx, cy = self.width / 2, self.height / 2

        arcade.draw_rect_filled(
            arcade.rect.XYWH(cx, cy, menu_w, menu_h),
            color=(25, 25, 35, 240)
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(cx, cy, menu_w, menu_h),
            color=MOCHA_LAVENDER,
            border_width=3
        )

        arcade.draw_text(
            "CHEAT MENU",
            x=cx,
            y=cy + 290,
            color=MOCHA_MAUVE,
            font_size=55,
            anchor_x="center",
            anchor_y="center",
            font_name="Handjet",
            bold=True
        )

        inv_status = 'ON' if self.player.invincible else 'OFF'
        power_status = 'ON' if self.player.is_powered_up else 'OFF'
        freeze_status = 'ON' if self.freeze_ghosts else 'OFF'
        cheats = [
            "[F1 / ESC] TO Close Menu",
            f"[F2] Toggle Invincibility: {inv_status}",
            f"[F3] Trigger Power Pellet: {power_status}",
            f"[F4] Toggle Freeze all ghosts: {freeze_status}",
            f"[F5] Toggle Debug: {'ON' if self.debug else 'OFF'}",
            f"[F6] Toggle Speed: {'ON' if self.speed_up else 'OFF'}",
            "[F7] Add +1 Life",
            "[F8] Skip the level",
        ]

        start_y = cy + 200
        for i, line in enumerate(cheats):
            arcade.draw_text(
                line,
                x=cx,
                y=start_y - (i * 70),
                # (i * 40) is how far from each other.
                color=arcade.color.WHITE,
                font_size=25,
                anchor_x="center",
                anchor_y="center",
                font_name="Handjet",
                bold=True
            )

    def on_text(self, text: str) -> None:
        """Forward text input events to the current level."""
        if hasattr(self.level_obj, 'on_text'):
            self.level_obj.on_text(text)

    def on_draw(self) -> None:
        """Render the entire game frame including HUD, maze, and entities."""
        self.clear()

        self.ui_camera.position = (
            self.width / 2 + self.shake_x,
            self.height / 2 + self.shake_y
        )
        self.ui_camera.use()

        # Draw the background image FIRST, strictly on the UI layer.
        self.draw_background_image()
        self.draw_ability()
        self.draw_cooldown_slider()
        for shockwave in self.shock:
            shockwave.draw()
        self.score_text.text = f"{self.score}"
        self.level_text.text = f"{self.level}"
        self.time_text.text = f"{int(self.timer)}s"
        self.score_text.draw()
        self.draw_hearts()
        self.level_text.draw()
        self.time_text.draw()

        # Calculate camera offset and rotation for the maze.
        if self.level != 4:
            self.camera.angle = 0

        screen_cx = self.width / 2
        screen_cy = self.height / 2

        maze_cx = self.offset_x + (self.cols * self.cell_size) / 2
        maze_cy = self.offset_y + (self.rows * self.cell_size) / 2

        angle = getattr(self.level_obj, 'current_angle',
                        0) if self.level == 4 else 0
        self.camera.angle = angle

        dx = maze_cx - screen_cx
        dy = maze_cy - screen_cy

        rad = math.radians(-angle)
        rot_dx = dx * math.cos(rad) - dy * math.sin(rad)
        rot_dy = dx * math.sin(rad) + dy * math.cos(rad)

        self.camera.position = (
            screen_cx + (dx - rot_dx) + self.shake_x,
            screen_cy + (dy - rot_dy) + self.shake_y
        )

        # use maze camera.
        self.camera.use()

        # Draw the maze background and effects
        self.draw_maze_background()
        self.level_obj.draw_effects(self)

        # Draw coins, player, and ghosts
        for coin in self.coins_lst:
            coin.draw()

        self.player_list.draw()
        self.blinky_list.draw()
        self.pinky_list.draw()
        self.inky_list.draw()
        self.clyde_list.draw()
        for sparkle in self.coin_sparkles:
            sparkle.draw()

        if self.debug:
            self.draw_debug()

        # Draw trail and particles.
        for trail in self.trail_particles:
            trail.draw()

        for particle in self.shatter_particles:
            particle.draw()
        for f in self.floating_scores:
            f.draw()
        self.ui_camera.use()

        # Draw top effects on the UI layer (stay fixed during rotation).
        self.level_obj.draw_top_effects(self)

        if self.cheat_menu:
            self.draw_cheat_menu()

        if self.pause:
            arcade.draw_rect_filled(
                arcade.rect.XYWH(self.width / 2, self.height /
                                 2, self.width, self.height),
                color=(10, 10, 20, 200)
            )
            self.manager.draw()

    def go_to_game_over(self) -> None:
        """Switch to the game over screen."""
        SoundManager.get().stop_music()
        self.shatter_particles.clear()
        self.player.visible = True
        self.game_over = GameOver(self.window, self.main_menu, self.score)
        self.window.show_view(self.game_over)

    def go_to_next_level(self) -> None:
        """Transition to the next level via the loading screen."""
        SoundManager.get().stop_music()
        from src.loading import LoadingView
        loading_view = LoadingView(
            self.window,
            self.main_menu,
            seed=self.level_obj.seed,
            level=self.level + 1,
            score=self.score,
            lives=self.player.lives,
        )
        self.window.show_view(loading_view)

    def go_to_victory(self) -> None:
        """Switch to the victory screen."""
        SoundManager.get().stop_music()
        self.vectory = Vectory(
            self.window,
            self.main_menu,
            self.score,
            self.level + 1,
            lives=self.player.lives,
            seed=self.level_obj.seed,
        )
        self.window.show_view(self.vectory)

    def ghosts_chase_player(self, delta_time: float) -> None:
        """Update all ghost AI chase logic for one frame."""

        self.blinky.chase_player(
            self.player,
            self.maze,
            self.cell_size,
            self.rows,
            self.cols,
            self.offset_x,
            self.offset_y,
            delta_time
        )

        self.pinky.chase_player(
            self.player,
            self.maze,
            self.cell_size,
            self.rows,
            self.cols,
            self.offset_x,
            self.offset_y,
            delta_time
        )

        self.inky.chase_player(
            self.player,
            self.maze,
            self.cell_size,
            self.rows,
            self.cols,
            self.offset_x,
            self.offset_y,
            delta_time,
            blinky=self.blinky
        )

        self.clyde.chase_player(
            self.player,
            self.maze,
            self.cell_size,
            self.rows,
            self.cols,
            self.offset_x,
            self.offset_y,
            delta_time
        )

    def on_update(self, delta_time: float) -> None:
        """Advance game logic by one frame: movement, collisions, timers."""

        self.shock = [s for s in self.shock if s.update(delta_time)]
        self.coin_sparkles = [
            p for p in self.coin_sparkles if p.update(delta_time)]
        if self.combo_timer > 0:
            self.combo_timer -= delta_time
            if self.combo_timer <= 0:
                self.combo_count = 0
                self.combo_timer = 0.0
                if not self.player.is_powered_up:
                    self.player.speed = self.player_speed

        self.trail_particles = [
            t for t in self.trail_particles if t.update(delta_time)]

        if (
            self.player.current_speed > self.player_speed
            and not self.player.is_dying
            and self.player.current_dir != (0, 0)
        ):
            self.trail_timer += delta_time
            if self.trail_timer >= self.TRAIL_INTERVAL:
                self.trail_timer = 0.0

                # Color: Golden Yellow if powered up, else Mauve.
                trail_color = (
                    (249, 226, 175)
                    if self.player.is_powered_up
                    else (203, 166, 247)
                )

                self.trail_particles.append(
                    TrailParticle(
                        x=self.player.center_x,
                        y=self.player.center_y,
                        texture=self.player.texture,
                        angle=self.player.angle,
                        width=self.player.width,
                        height=self.player.height,
                        color=trail_color,
                        lifetime=0.22
                    )
                )

        if self.pause or self.cheat_menu:
            return
        if self.player.is_powered_up and self.is_hit:
            self.trigger_shake(0.3, 30)
            self.is_hit = False
        elif self.player.is_powered_up:
            self.trigger_shake(999, 2)
        else:
            self.trigger_shake(0, 0)
        self.floating_scores = [
            f for f in self.floating_scores if f.update(delta_time)]
        if self.shake_time > 0:
            self.shake_time -= delta_time
            self.shake_x = random.uniform(-self.shake_intensity,
                                          self.shake_intensity)
            self.shake_y = random.uniform(-self.shake_intensity,
                                          self.shake_intensity)
        else:
            self.shake_x = 0
            self.shake_y = 0
        if self.shatter_particles:
            self.shatter_particles = [
                p for p in self.shatter_particles if p.update(delta_time)]
            if not self.shatter_particles:
                if self.player.lives <= 0:
                    self.go_to_game_over()
                else:
                    self.respawn_after_death()
            return

        if self.player.is_dying:
            self.player.update_animation(delta_time)
            if not self.player.is_dying:
                self.player.visible = False
                self.shatter_particles = [
                    ShatterParticle(self.player.center_x, self.player.center_y)
                    for _ in range(16)
                ]
            return

        self.level_obj.update(self, delta_time)

        if self.collected_coins == self.target_coins:
            if self.level < self.config_parser.max_level:
                self.go_to_next_level()
            else:
                self.go_to_victory()
            return

        self.timer -= delta_time
        if self.timer < 0.80:
            self.go_to_game_over()
            return

        # Ability timers
        for ability in self.ability_defs:
            if ability["active_timer"] > 0:
                ability["active_timer"] = max(
                    0.0, ability["active_timer"] - delta_time)
            if ability["cooldown_timer"] > 0:
                ability["cooldown_timer"] = max(
                    0.0, ability["cooldown_timer"] - delta_time)

        self.player.update_grid_movement(
            self.maze,
            self.cell_size,
            self.rows,
            self.cols,
            self.offset_x,
            self.offset_y,
            delta_time,
        )
        self.player.update_animation(delta_time)

        active_stop_time = self.get_ability_by_key(arcade.key.Q)
        active_frost_walk = self.get_ability_by_key(arcade.key.E)

        if not self.freeze_ghosts and (
            active_stop_time is None
            or active_stop_time["active_timer"] <= 0
        ):
            ghost_dt = (
                delta_time * 0.4
                if active_frost_walk is not None
                and active_frost_walk["active_timer"] > 0
                else delta_time
            )
            self.ghosts_chase_player(ghost_dt)
        self.check_ghost_collisions()
        self.reset_ghost_colors()

        for coin in self.coins_lst:
            if not coin.is_eaten:
                distance = math.hypot(
                    self.player.center_x - coin.x,
                    self.player.center_y - coin.y,
                )
                if distance < (self.player.width / 2 + coin.radius):
                    coin.is_eaten = True
                    for _ in range(4):
                        self.coin_sparkles.append(CoinSparkle(coin.x, coin.y))
                    if coin.is_powerup:
                        self.score += getattr(self.level_obj,
                                              "points_per_super_pacgum", 50)
                        self.player.activate_power_up(self.power_time)
                        SoundManager.get().play_sfx("power_pellet")
                        self.shock.append(
                            Shockwave(coin.x, coin.y, color=(203, 166, 247))
                        )
                    else:
                        self.score += getattr(self.level_obj,
                                              "points_per_pacgum", 10)
                        SoundManager.get().play_sfx("coin")
                    self.combo_count += 1
                    self.combo_timer = self.combo_limit
                    multiplier = (self.combo_count // 10) + 1
                    bonus = 1.0 + min(0.4, (multiplier - 1) * 0.1)
                    self.player.speed = self.player_speed * bonus
                    if self.combo_count >= 10 and self.combo_count % 10 == 0:
                        self.floating_scores.append(
                            Floating_score(
                                self.player.center_x,
                                self.player.center_y + 15,
                                f"x{multiplier} COMBO!",
                                MOCHA_RED
                            )
                        )

                    self.collected_coins += 1

    def check_ghost_collisions(self) -> None:
        """Handles Pac-Man <-> ghost contact: taking damage or eating a scared
        ghost.
        """
        if self.player.is_dying or self.shatter_particles:
            return

        for ghost in (self.blinky, self.pinky, self.inky, self.clyde):
            if ghost.state == "EATEN":
                continue

            distance = math.hypot(
                self.player.center_x - ghost.center_x,
                self.player.center_y - ghost.center_y,
            )
            if distance >= (self.player.width / 2 + ghost.width / 2):
                continue

            if ghost.state == "FRIGHTENED":
                self.combo_count += 1
                self.combo_timer = self.combo_limit
                self.score += getattr(self.level_obj, "points_per_ghost", 200)
                ghost.get_hit()
                SoundManager.get().play_sfx("ghost_eaten")
                self.floating_scores.append(
                    Floating_score(
                        ghost.center_x, ghost.center_y, "+200", MOCHA_RED)
                )
                self.is_hit = True
            elif (not self.player.invincible) and ghost.can_damage:
                self.handle_player_hit()
                break

    def handle_player_hit(self) -> None:
        """Process the player taking damage from a ghost."""
        if (
            self.player.is_dying
            or self.shatter_particles
            or self.player.invincible
        ):
            return
        SoundManager.get().play_sfx("death")
        self.combo_count = 0
        self.combo_timer = 0.0
        self.player.speed = self.player_speed
        self.trigger_shake(0.3, 8)
        self.player.take_damage()
        self.player.start_death_animation()

    def respawn_after_death(self) -> None:
        """Reset player and ghosts to spawn positions after a death."""
        self.shatter_particles.clear()
        self.player.visible = True
        self.player.respawn_at(self.player_spawn_x, self.player_spawn_y)
        self.player.invincible = True
        self.player.invincible_timer = 2.0
        self.player.just_took_damage = True
        self.player.damage_invincibility_duration = 2.0
        for ability in self.ability_defs:
            ability["active_timer"] = 0.0
            ability["cooldown_timer"] = 0.0

        for ghost in (self.blinky, self.pinky, self.inky, self.clyde):
            if ghost.state == "EATEN":
                continue
            x, y = ghost.get_cell_center(
                ghost.home_row,
                ghost.home_col,
                self.cell_size,
                self.rows,
                self.offset_x,
                self.offset_y,
            )
            ghost.center_x = ghost.target_x = x
            ghost.center_y = ghost.target_y = y
            ghost.state = "CHASE"
            ghost.color = (255, 255, 255)
            ghost.texture = arcade.load_texture(ghost.normal_texture_path)

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Handle key release events for player and level logic."""
        if self.level == 5 and hasattr(self.level_obj, 'key_release'):
            self.level_obj.key_release(key, self)
            return
        else:
            level_key = self.level_obj.key_release(key, self)
        if level_key is not None:
            key = level_key

        self.player.on_key_release(key)

    def on_show_view(self) -> None:
        """Start music and set up the pause menu UI when the view appears."""
        SoundManager.get().play_music("gameplay", loop=True)
        self.manager.enable()

        menu_elements = arcade.gui.UIBoxLayout(space_between=40)

        # button style.
        button_style = {
            "normal": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name="Handjet",
                font_color=(*MOCHA_TEXT, 255),
                bg=(*MOCHA_SURFACE0, 255),
                border=(*MOCHA_MAUVE, 255),
                border_width=2,
            ),
            "hover": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name="Handjet",
                font_color=(*MOCHA_TEXT, 255),
                bg=(*MOCHA_SURFACE1, 255),
                border=(*MOCHA_LAVENDER, 255),
                border_width=2,
            ),
            "press": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name="Handjet",
                font_color=(*MOCHA_TEXT, 255),
                bg=(*MOCHA_MANTLE, 255),
                border=(*MOCHA_MAUVE, 255),
                border_width=3,
            ),
            "disabled": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name="Handjet",
                font_color=(120, 118, 136, 255),
                bg=(*MOCHA_CRUST, 255),
                border=(56, 64, 96, 255),
                border_width=1,
            )
        }

        # init the buttons.
        resume_game = arcade.gui.UIFlatButton(
            text="RESUME GAME", width=300, height=100, style=button_style)
        quit_game = arcade.gui.UIFlatButton(
            text="MAIN_MENU", width=300, height=100, style=button_style)

        # nested function to do things if the buttons was clicked.
        @resume_game.event("on_click")
        def on_click_start(event: arcade.gui.UIOnClickEvent) -> None:
            # This is the action! Swap from current menu view to game view.
            SoundManager.get().play_sfx("menu_select")
            self.pause = False

        @quit_game.event("on_click")
        def on_click_quit(event: arcade.gui.UIOnClickEvent) -> None:
            SoundManager.get().play_sfx("menu_select")
            SoundManager.get().stop_music()
            self.window.show_view(self.main_menu)
            self.pause = False

        # adding buttons to one group layout.
        menu_elements.add(resume_game)
        menu_elements.add(quit_game)

        # give the group to the manager.
        self.manager.add(
            arcade.gui.UIAnchorLayout(
                anchor_x="center_x",
                anchor_y="center_y",
                children=[menu_elements]
            )
        )

    def on_hide_view(self) -> None:
        """Stop music and disable the UI manager when the view is hidden."""
        SoundManager.get().stop_music()
        self.manager.disable()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle key presses for menus, cheats, abilities, and movement."""
        if key == arcade.key.ESCAPE:
            if self.cheat_menu:
                self.cheat_menu = False
            elif self.pause or not self.pause:
                self.pause = (not self.pause)
            return

        if self.pause or self.player.is_dying or self.shatter_particles:
            return

        if key == arcade.key.F1:
            self.cheat_menu = (not self.cheat_menu)

        if key == arcade.key.F2:
            if self.cheat_menu:
                self.player.invincible_cheat = (
                    not self.player.invincible_cheat
                )
                self.player.invincible = self.player.invincible_cheat
                self.player.invincible_timer = (
                    9999999999999999 if self.player.invincible else 0
                )
                self.player.just_took_damage = False
                self.player.alpha = 255

        if key == arcade.key.F3:
            if self.cheat_menu:
                self.player.is_powered_up = (not self.player.is_powered_up)
                self.player.power_timer = (
                    99999999999999999 if self.player.is_powered_up else 0
                )

        if key == arcade.key.F4:
            if self.cheat_menu:
                self.freeze_ghosts = (not self.freeze_ghosts)

        if key == arcade.key.F5:
            if self.cheat_menu:
                if self.debug:
                    self.debug = False
                else:
                    self.debug = True

        if key == arcade.key.F6:
            if self.cheat_menu:
                self.speed_up = (not self.speed_up)
                self.player.speed = self.player_speed * \
                    2 if self.speed_up else self.player_speed

        if key == arcade.key.F7:
            if self.cheat_menu:
                self.player.lives += 1

        if key == arcade.key.F8:
            if self.cheat_menu:
                if self.level < self.config_parser.max_level:
                    self.go_to_next_level()
                else:
                    self.go_to_victory()

        if key in (arcade.key.E, arcade.key.Q, arcade.key.F):
            self.trigger_ability(key)
            return

        if hasattr(self.level_obj, 'key_press'):
            if self.level == 5:
                self.level_obj.key_press(key, self)
                return
            else:
                key = self.level_obj.key_press(key)

        self.player.on_key_press(key)
