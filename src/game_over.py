from typing import Any
import pathlib
import arcade
import arcade.gui
from src.score import Score
from src.sound_manager import SoundManager


BASE_WIDTH = 1920
BASE_HEIGHT = 1200


class GameOver(arcade.View):
    """Game over view displaying final score and name entry."""

    def __init__(
        self, window: arcade.Window, main_menu: Any, score: int
    ) -> None:
        """Initialize the game over view, UI layout, and score system."""
        super().__init__()
        SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()

        self.main_menu = main_menu
        self.window = window
        self.background = arcade.load_texture("src/assets/game0ver.png")

        self.manager = arcade.gui.UIManager()
        self.score = score
        self.score_class = Score()
        self.player_name = ""
        self.score_saved = False
        font_path = (
            SCRIPT_DIR / "assets" / "Handjet" / "static" / "Handjet-Bold.ttf"
        )
        arcade.load_font(str(font_path))
        self.selected_option = 0

    @property
    def x_center(self) -> float:
        """Return dynamic horizontal center of the window."""
        return float(self.window.width / 2)

    @property
    def y_center(self) -> float:
        """Return dynamic vertical center of the window."""
        return float(self.window.height / 2)

    def save_score_once(self) -> None:
        """Persist the entered score a single time per game-over screen."""
        if self.score_saved:
            return

        name = self.player_name.strip()
        if not name:
            return

        self.score_class.write_score(name, self.score)
        self.score_saved = True

    def on_show_view(self) -> None:
        """Play game over sound effect when view appears."""
        SoundManager.get().play_sfx("game_over")

    def on_draw(self) -> None:
        """Render the game over background, score, and entered name."""
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
            ))
        arcade.draw_text(
            f"{self.score}",
            1112 * scale_x,
            695 * scale_y,
            (180, 190, 254),
            font_size=max(1, int(42 * font_scale)),
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center"
        )
        arcade.draw_text(
            f"{self.player_name.upper()}",
            1006 * scale_x,
            595 * scale_y,
            (180, 190, 254),
            font_size=max(1, int(42 * font_scale)),
            font_name="Handjet",
            bold=True,
            anchor_x="left",
            anchor_y="center",
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle keyboard input for name entry and option navigation."""
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.TAB):
            self.selected_option ^= 1
            SoundManager.get().play_sfx("menu_select")

        elif key == arcade.key.ENTER:
            SoundManager.get().play_sfx("menu_select")
            self.save_score_once()
            if self.selected_option == 0:
                self.main_menu.new_game()
            else:
                self.window.show_view(self.main_menu)

        elif key == arcade.key.ESCAPE:
            SoundManager.get().play_sfx("menu_select")
            self.main_menu.new_game()

        elif key == arcade.key.BACKSPACE:
            self.player_name = self.player_name[:-1]

        elif len(self.player_name) < 10 and (
            chr(key).isalnum() or key == arcade.key.SPACE
        ):
            self.player_name += chr(key).upper()

    def on_mouse_press(
        self, x: float, y: float, button: int, modifiers: int
    ) -> None:
        """Handle mouse click events on menu buttons."""
        scale_x = self.window.width / BASE_WIDTH
        scale_y = self.window.height / BASE_HEIGHT

        if x >= 1600 * scale_x:
            if name := self.player_name.strip():
                self.score_class.write_score(name, self.score)

            if 720 * scale_y <= y <= 807 * scale_y:
                SoundManager.get().play_sfx("menu_select")
                self.main_menu.new_game(seed=42)
            elif 435 * scale_y <= y <= 520 * scale_y:
                SoundManager.get().play_sfx("menu_select")
                self.window.show_view(self.main_menu)
