import arcade
import pathlib
from src.score import Score
from src.loading import LoadingView
from src.sound_manager import SoundManager

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
BASE_WIDTH = 1920
BASE_HEIGHT = 1200


class Vectory(arcade.View):
    """Victory View shown upon completing the game."""

    def __init__(
        self,
        window: arcade.Window,
        main_menu: arcade.View,
        score: int,
        next_level: int,
        lives: int | None = None,
        seed: int | None = None,
    ) -> None:
        """Initialize victory view state, scores, and fonts."""
        super().__init__()

        self.main_menu = main_menu
        self.window = window

        self.score = score
        self.score_class = Score()
        self.next_level = next_level
        self.lives = lives
        self.player_name = ""
        self.seed = seed
        self.background = arcade.load_texture("src/assets/Desktop - 4.png")

        font_path = (
            SCRIPT_DIR / "assets" / "Handjet" / "static" / "Handjet-Bold.ttf"
        )
        if font_path.exists():
            arcade.load_font(str(font_path))

    @property
    def x_center(self) -> float:
        """Return dynamic horizontal center of the window."""
        return float(self.window.width / 2)

    @property
    def y_center(self) -> float:
        """Return dynamic vertical center of the window."""
        return float(self.window.height / 2)

    def get_max_level(self) -> int:
        """Return the maximum allowed level from config or default."""
        cfg = getattr(self.main_menu, "config_parser", None)
        return cfg.max_level if cfg else 10

    def go_to_next_level(self) -> None:
        """Advance to the next level loading view."""
        SoundManager.get().play_sfx("menu_select")
        if self.next_level <= self.get_max_level():
            loading_view = LoadingView(
                self.window,
                self.main_menu,
                seed=self.seed if self.seed is not None else 42,
                level=self.next_level,
                score=self.score,
                lives=self.lives,
            )
            self.window.show_view(loading_view)

    def restart_game(self) -> None:
        """Save score and restart the game from level 1."""
        SoundManager.get().play_sfx("menu_select")
        name = self.player_name.strip() or "PLAYER"
        self.score_class.write_score(name, self.score)
        seed = self.seed if self.seed is not None else 42
        new_game_fn = getattr(self.main_menu, "new_game", None)
        if callable(new_game_fn):
            new_game_fn(seed=seed)
        else:
            loading_view = LoadingView(
                self.window,
                self.main_menu,
                seed=seed,
                level=1,
            )
            self.window.show_view(loading_view)

    def on_draw(self) -> None:
        """Render the victory screen, score, and player name."""
        self.clear()
        scale_x = self.window.width / BASE_WIDTH
        scale_y = self.window.height / BASE_HEIGHT
        font_scale = min(scale_x, scale_y)

        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(
                0,
                0,
                self.window.width,
                self.window.height,
            ),
        )
        arcade.draw_text(
            f"{self.score}",
            960 * scale_x,
            1144 * scale_y,
            arcade.color.GOLD,
            font_size=max(1, int(40 * font_scale)),
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        has_name = bool(self.player_name)
        display_name = self.player_name.upper() if has_name else "TYPE NAME"
        arcade.draw_text(
            f"{display_name}",
            self.x_center + 5 * scale_x,
            self.y_center - 40 * scale_y,
            (180, 190, 254),
            font_size=max(1, int(36 * font_scale)),
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle keyboard navigation and name input."""
        if key == arcade.key.ENTER:
            SoundManager.get().play_sfx("menu_select")
            name = self.player_name.strip() or "PLAYER"
            self.score_class.write_score(name, self.score)
            self.window.show_view(self.main_menu)
        elif key == arcade.key.ESCAPE:
            SoundManager.get().play_sfx("menu_select")
            self.window.show_view(self.main_menu)
        elif key == arcade.key.BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif len(self.player_name) < 10 and (
            chr(key).isalnum() or key == arcade.key.SPACE
        ):
            self.player_name += chr(key).upper()

    def on_mouse_press(
        self, x: float, y: float, button: int, modifiers: int
    ) -> None:
        """Handle button clicks to retry from level 1 or return to menu."""
        scale_x = self.window.width / BASE_WIDTH
        scale_y = self.window.height / BASE_HEIGHT

        if 845 * scale_x <= x <= 1084 * scale_x:
            if 389 * scale_y <= y <= 458 * scale_y:
                self.restart_game()
            elif 288 * scale_y <= y <= 353 * scale_y:
                SoundManager.get().play_sfx("menu_select")
                name = self.player_name.strip() or "PLAYER"
                self.score_class.write_score(name, self.score)
                self.window.show_view(self.main_menu)
