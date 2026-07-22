from typing import List, Dict
import json
import arcade
import arcade.gui

#game over view prototype.
class GameOver(arcade.View):
    def __init__(self, window: arcade.Window, main_menu: arcade.View):
        super().__init__()

        self.main_menu = main_menu
        self.window = window

        self.x_center = self.width / 2
        self.y_center = self.height / 2
    
    
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK_OLIVE)
    
    #what will draw.
    def on_draw(self):

        #clear the screen before drawing new things to prevent overdrawing on last view.
        self.clear()

        #draw circle
        arcade.draw_circle_filled(self.x_center , self.y_center, 15, arcade.color.RED)

        arcade.draw_text("Game Over!", self.x_center, self.y_center + 100, arcade.color.RED, font_size=100, anchor_x="center", anchor_y="center")
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu)
