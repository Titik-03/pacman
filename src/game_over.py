from typing import List, Dict
import json
import arcade
import arcade.gui
from src.score import Score

#game over view prototype.
class GameOver(arcade.View):
    def __init__(self, window: arcade.Window, main_menu: arcade.View, score: int):
        super().__init__()

        self.main_menu = main_menu
        self.window = window

        self.x_center = self.width / 2
        self.y_center = self.height / 2

        self.manager = arcade.gui.UIManager()
        self.score = score
        self.score_class = Score()

    
    
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK_OLIVE)

        self.manager.enable()

        #Build layout.
        layout = arcade.gui.UIAnchorLayout()
        box = arcade.gui.UIBoxLayout(space_between=15)
        
        # Score Label
        score_label = arcade.gui.UILabel(
            text=f"Score: {self.score}", 
            font_size=20,
            text_color=arcade.color.YELLOW,
        )


        box.add(score_label)

        name = arcade.gui.UILabel(
                    text="Enter you name.", 
                    font_size=20,
                    text_color=arcade.color.WHITE
                )
        box.add(name)
        
        #Input Text Field
        self.input_field = arcade.gui.UIInputText(
            width=250, 
            height=40, 
            font_size=16
        )

        box.add(self.input_field)
        
        #Submit Button
        submit_btn = arcade.gui.UIFlatButton(text="Confirm", width=200)
        restart_btn = arcade.gui.UIFlatButton(text="Restart", width=200)

        box.add(submit_btn)
        box.add(restart_btn)


        #Bind button click event
        @submit_btn.event("on_click")
        def on_click_submit(event):
            player_name = self.input_field.text.strip()
            if player_name:
                self.score_class.write_score(player_name, self.score)
                self.window.show_view(self.main_menu)

        @restart_btn.event("on_click")
        def on_click_submit(event):
            self.main_menu.new_game()

        layout.add(box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(layout)


    def on_hide_view(self):
        self.manager.disable()


    #what will draw.
    def on_draw(self):

        #clear the screen before drawing new things to prevent overdrawing on last view.
        self.clear()

        #draw circle
        # arcade.draw_circle_filled(self.x_center , self.y_center, 15, arcade.color.RED)

        arcade.draw_text("Game Over!", self.x_center, self.y_center + 400, arcade.color.RED, font_size=100, anchor_x="center", anchor_y="center")

        self.manager.draw()



    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            player_name = self.input_field.text.strip()
            if player_name:
                self.score_class.write_score(player_name, self.score)
                self.window.show_view(self.main_menu)
        if key == arcade.key.ESCAPE:
            self.main_menu.new_game()

