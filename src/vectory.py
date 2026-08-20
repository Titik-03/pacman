import random
from typing import List, Dict
import json
import arcade
import arcade.gui
from src.score import Score
from src.loading import LoadingView


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

        self.manager = arcade.gui.UIManager()
        self.score = score
        self.score_class = Score()
        self.next_level = next_level
        self.lives = lives
        self.input_field = None
        self.seed = seed

    def go_to_next_level(self):
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

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK_OLIVE)

        self.manager.enable()

        #Build layout.
        layout = arcade.gui.UIAnchorLayout()
        box = arcade.gui.UIBoxLayout(space_between=20)

        score_label = arcade.gui.UILabel(
            text=f"Current Score: {self.score}",
            font_size=28,
            text_color=arcade.color.YELLOW,
            font_name="Handjet",
            bold=True,
        )
        box.add(score_label)

        if self.next_level <= 10:
            next_btn = arcade.gui.UIFlatButton(
                text=f"NEXT LEVEL ({self.next_level})", width=260, height=60
            )
            @next_btn.event("on_click")
            def on_click_next(event):
                self.go_to_next_level()

            box.add(next_btn)

            menu_btn = arcade.gui.UIFlatButton(text="MAIN MENU", width=260, height=50)
            @menu_btn.event("on_click")
            def on_click_menu(event):
                self.window.show_view(self.main_menu)

            box.add(menu_btn)
        else:
            name_label = arcade.gui.UILabel(
                text="Enter your name for High Score:",
                font_size=22,
                text_color=arcade.color.WHITE,
                font_name="Handjet",
            )
            box.add(name_label)

            self.input_field = arcade.gui.UIInputText(
                width=280, height=45, font_size=20
            )
            box.add(self.input_field)

            submit_btn = arcade.gui.UIFlatButton(text="Confirm & Exit", width=220)
            @submit_btn.event("on_click")
            def on_click_submit(event):
                player_name = self.input_field.text.strip() if self.input_field else ""
                if player_name:
                    self.score_class.write_score(player_name, self.score)
                    self.window.show_view(self.main_menu)

            box.add(submit_btn)

        layout.add(box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(layout)

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        title_text = (
            f"LEVEL {self.next_level - 1} CLEARED!"
            if self.next_level <= 10
            else "VICTORY! GAME COMPLETE!"
        )
        arcade.draw_text(
            title_text,
            self.x_center,
            self.y_center + 260,
            arcade.color.GOLD,
            font_size=60,
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            if self.next_level <= 10:
                self.go_to_next_level()
            elif self.input_field:
                player_name = self.input_field.text.strip()
                if player_name:
                    self.score_class.write_score(player_name, self.score)
                    self.window.show_view(self.main_menu)

                


