from typing import List, Dict
import json
import arcade
import arcade.gui
from src.score import Score
import pathlib

#game over view prototype.
class GameOver(arcade.View):
    def __init__(self, window: arcade.Window, main_menu: arcade.View, score: int):
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
        font_path = SCRIPT_DIR / "assets" / "Handjet" / "static" / "Handjet-Bold.ttf"
        arcade.load_font(str(font_path))
        self.selected_option = 0



        self.mouse_x = 0.0
        self.mouse_y = 0.0

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x = x
        self.mouse_y = y
    
    def on_draw(self):

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
        arcade.draw_text(
            f"Mouse: X={int(self.mouse_x)}, Y={int(self.mouse_y)}",
            10,
            10,
            arcade.color.YELLOW,
            font_size=18,
            bold=True
        )

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.TAB):
            self.selected_option = 1 - self.selected_option
            return

        if key == arcade.key.ENTER:
            player_name = self.player_name.strip()
            if player_name:
                self.score_class.write_score(player_name, self.score)
            
            if self.selected_option == 0:
                self.main_menu.new_game(seed=42)
            else:
                self.window.show_view(self.main_menu)
            return

        if key == arcade.key.ESCAPE:
            self.main_menu.new_game(seed=42)
            return

        if key == arcade.key.BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif len(self.player_name) < 10:
            if arcade.key.A <= key <= arcade.key.Z:
                self.player_name += chr(key).upper()
            elif arcade.key.KEY_0 <= key <= arcade.key.KEY_9:
                self.player_name += chr(key)
            elif key == arcade.key.SPACE:
                self.player_name += " "

    def on_mouse_press(self, x, y, button, modifiers):
        # Top-right button (RETRY LEVEL)
        if abs(x - (self.x_center + 420)) < 120 and abs(y - (self.y_center + 30)) < 30:
            player_name = self.player_name.strip()
            if player_name:
                self.score_class.write_score(player_name, self.score)
            self.main_menu.new_game(seed=42)

        # Bottom-right button (MAIN MENU)
        elif abs(x - (self.x_center + 420)) < 120 and abs(y - (self.y_center - 65)) < 30:
            player_name = self.player_name.strip()
            if player_name:
                self.score_class.write_score(player_name, self.score)
            self.window.show_view(self.main_menu)