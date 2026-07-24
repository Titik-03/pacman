import arcade
import arcade.gui
from score import Score
from typing import List
from pause_menu import PauseMenu
from game_over import GameOver
from vectory import Vectory


#Game test view.
class Game(arcade.View):

    #init with deafults.
    def __init__(self, menu: arcade.View, window: arcade.Window):
        super().__init__()

        self.x_center = self.width / 2
        self.y_center = self.height / 2
    
        self.Game_text = arcade.Text(
            text="Main Game here.",
            x = self.width / 2,
            y = self.height - 200,
            color=arcade.color.WHITE,
            font_size=150,
            anchor_x="center"
        )

        self.manager = arcade.gui.UIManager()

        self.main_menu = menu
        self.window = window
        self.pause_menu = PauseMenu(self)
        self.pause = False
        self.score = 11  #has to be changing


    #what will happen if the view is showed.
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK_OLIVE)

        self.manager.enable()

        menu_elements = arcade.gui.UIBoxLayout(space_between=40)

        #button style.
        button_style = {
            "normal": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name=("georgia", "times new roman", "serif"),
                font_color=(234, 236, 250),
                bg=(20, 12, 48),
                border=(90, 72, 160),
                border_width=2,
            ),
            "hover": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name=("georgia", "times new roman", "serif"),
                font_color=(250, 250, 255),
                bg=(64, 32, 120),
                border=(180, 170, 255),
                border_width=2,
            ),
            "press": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name=("georgia", "times new roman", "serif"),
                font_color=(252, 244, 255),
                bg=(8, 6, 26),
                border=(110, 78, 190),
                border_width=3,
            ),
            "disabled": arcade.gui.UIFlatButton.UIStyle(
                font_size=20,
                font_name=("georgia", "times new roman", "serif"),
                font_color=(120, 118, 136),
                bg=(18, 18, 36),
                border=(56, 64, 96),
                border_width=1,
            )
        }

        #init the buttons.
        resume_game = arcade.gui.UIFlatButton(text="RESUME GAME", width=300, height=100, style=button_style)
        quit_game = arcade.gui.UIFlatButton(text="MAIN_MENU", width=300, height=100, style=button_style)
        
        #settings if future needed.
        # settings = arcade.gui.UIFlatButton(text="SETTINGS", width=300, height=100, style=button_style)

        #nested function to do things if the buttons was clicked.
        @resume_game.event("on_click")
        def on_click_start(event):
            #This is the action! Swap from current menu view to game view.
            self.pause = False
        
        #settings if futur needed.
        # @settings.event("on_click")
        # def on_click_high_score(event):
        #     #This is the action! Swap from current menu view to game view.
        #     self.window.show_view(self.settings)
        
        @quit_game.event("on_click")
        def on_click_quit(event):
            self.window.show_view(self.main_menu)
            self.pause = False

        #adding buttons to one group layout.
        menu_elements.add(resume_game)
        menu_elements.add(quit_game)

        #settings if futur needed...
        # menu_elements.add(settings)

        #give the group to the manager.
        self.manager.add(
            arcade.gui.UIAnchorLayout(
                anchor_x="center_x",
                anchor_y="center_y",
                children=[menu_elements]
            )
        )

    def on_hide_view(self):
        self.manager.disable()
    

    def on_update(self, delta_time):
        if self.pause:
            return


    #what will draw.
    def on_draw(self):

        #clear the screen before drawing new things to prevent overdrawing on last view.
        self.clear()

        #draw circle
        arcade.draw_circle_filled(self.x_center , self.y_center, 15, arcade.color.RED)

        self.Game_text.draw()

        if self.pause:
            self.manager.draw()
        



    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.pause == False:
                self.pause = True
            else:
                self.pause = False
        if key == arcade.key.F1:     #this is just for testing. Has to be changed!!!!
            self.game_over = GameOver(self.window, self.main_menu, self.score)
            self.window.show_view(self.game_over)

        if key == arcade.key.F2:
            self.vectory = Vectory(self.window, self.main_menu, self.score)
            self.window.show_view(self.vectory)
