import arcade
import pathlib
from src.score import Score
from src.loading import LoadingView
from src.sound_manager import SoundManager

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


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

        self.x_center = self.width / 2
        self.y_center = self.height / 2

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

    def on_draw(self) -> None:
        """Render the victory screen, score, and player name."""
        self.clear()
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
            960,
            1144,
            arcade.color.GOLD,
            font_size=40,
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        has_name = bool(self.player_name)
        display_name = self.player_name.upper() if has_name else "TYPE NAME"
        arcade.draw_text(
            f"{display_name}",
            self.x_center + 5,
            self.y_center - 40,
            (180, 190, 254),
            font_size=36,
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
        """Handle button clicks to continue or return to menu."""
        if 845 <= x <= 1084:
            if 458 >= y >= 389:
                if self.next_level <= self.get_max_level():
                    self.go_to_next_level()
                else:
                    name = self.player_name.strip() or "PLAYER"
                    self.score_class.write_score(name, self.score)
                    self.window.show_view(self.main_menu)
            elif 353 >= y >= 288:
                SoundManager.get().play_sfx("menu_select")
                self.window.show_view(self.main_menu)
