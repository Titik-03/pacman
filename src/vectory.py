import random
from typing import List, Dict
import json
import arcade
import arcade.gui
from src.score import Score
from src.loading import LoadingView
from src.sound_manager import SoundManager


class Vectory(arcade.View):
    def __init__(
        self,
        window: arcade.Window,
        main_menu: arcade.View,
        score: int,
        next_level: int,
        lives: int = None,
        seed: int = None,
    ):
        super().__init__()

        self.main_menu = main_menu
        self.window = window

        self.x_center = self.width / 2
        self.y_center = self.height / 2

        self.score = score
        self.score_class = Score()
        self.next_level = next_level
        self.lives = lives
        self.input_field = None
        self.seed = seed
        self.background = arcade.load_texture("src/assets/bgv.png")
        self.x = 0
        self.y = 0
        

    def go_to_next_level(self):
        SoundManager.get().play_sfx("menu_select")
        if self.next_level <= 10:
            loading_view = LoadingView(
                self.window,
                self.main_menu,
                seed=self.seed,
                level=self.next_level,
                score=self.score,
                lives=self.lives,
            )
            self.window.show_view(loading_view)

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
            self.score,
            self.x_center + 15,
            1020,
            arcade.color.GOLD,
            font_size=40,
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            f"{self.x}, {self.y}",
            10,
            10,
            arcade.color.BLACK,
            font_size=60,
            font_name="Handjet",
            bold=True,
            anchor_x="left",
            anchor_y="bottom",
        )
        

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            if self.next_level <= 10:
                self.go_to_next_level()
            elif self.input_field:
                player_name = self.input_field.text.strip()
                if player_name:
                    self.score_class.write_score(player_name, self.score)
                    self.window.show_view(self.main_menu)

    def on_mouse_press(self, x, y, button, modifiers):
        if 764 <= x <= 1167:
            if 373 >= y >= 311:
                self.go_to_next_level()
            elif 273 >= y >= 211:
                SoundManager.get().play_sfx("menu_select")
                self.window.show_view(self.main_menu)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        self.x = x
        self.y = y