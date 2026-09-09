from typing import Any
import pathlib
import arcade
import arcade.gui
from src.score import Score
from src.sound_manager import SoundManager


class GameOver(arcade.View):
    def __init__(
        self, window: arcade.Window, main_menu: Any, score: int
    ) -> None:
        super().__init__()
        SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()

        self.main_menu = main_menu
        self.window = window
        self.background = arcade.load_texture("src/assets/game0ver.png")

        self.x_center = self.width / 2
        self.y_center = self.height / 2

        self.manager = arcade.gui.UIManager()
        self.score = score
        self.score_class = Score()
        self.player_name = ""
        font_path = (
            SCRIPT_DIR / "assets" / "Handjet" / "static" / "Handjet-Bold.ttf"
        )
        arcade.load_font(str(font_path))
        self.selected_option = 0

    def on_show_view(self) -> None:
        SoundManager.get().play_sfx("game_over")

    def on_draw(self) -> None:

        self.clear()
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
            self.x_center + 110,
            self.y_center + 60,
            (180, 190, 254),
            font_size=42,
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center"
        )
        arcade.draw_text(
            f"{self.player_name.upper()}",
            self.x_center + 100,
            self.y_center - 30,
            (180, 190, 254),
            font_size=42,
            font_name="Handjet",
            bold=True,
            anchor_x="left",
            anchor_y="center",
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.TAB):
            self.selected_option ^= 1
            SoundManager.get().play_sfx("menu_select")

        elif key == arcade.key.ENTER:
            SoundManager.get().play_sfx("menu_select")
            if name := self.player_name.strip():
                self.score_class.write_score(name, self.score)
            if self.selected_option == 0:
                self.main_menu.new_game(seed=42)
            else:
                self.window.show_view(self.main_menu)

        elif key == arcade.key.ESCAPE:
            SoundManager.get().play_sfx("menu_select")
            self.main_menu.new_game(seed=42)

        elif key == arcade.key.BACKSPACE:
            self.player_name = self.player_name[:-1]

        elif len(self.player_name) < 10 and (
            chr(key).isalnum() or key == arcade.key.SPACE
        ):
            self.player_name += chr(key).upper()

    def on_mouse_press(
        self, x: float, y: float, button: int, modifiers: int
    ) -> None:
        if x >= 1481:
            if name := self.player_name.strip():
                self.score_class.write_score(name, self.score)

            if 560 <= y <= 690:
                SoundManager.get().play_sfx("menu_select")
                self.main_menu.new_game(seed=42)
            elif 250 <= y <= 390:
                SoundManager.get().play_sfx("menu_select")
                self.window.show_view(self.main_menu)
