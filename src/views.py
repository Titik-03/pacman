import arcade
import arcade.gui
from score import Score
from typing import List

#Game test view.
class Game(arcade.View):

    #init with deafults.
    def __init__(self):
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

    #what will happen if the view is showed.
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK_OLIVE)
    
    #what will draw.
    def on_draw(self):

        #clear the screen before drawing new things to prevent overdrawing on last view.
        self.clear()

        #draw circle
        arcade.draw_circle_filled(self.x_center , self.y_center, 15, arcade.color.RED)

        self.Game_text.draw()


#Game test view.
class HighScore(arcade.View):

    #init with deafults.
    def __init__(self):
        super().__init__()

        self.x_center = self.width / 2
        self.y_center = self.height / 2
    
        self.high_score_text = arcade.Text(
            text="High_score.",
            x = self.width / 2,
            y = self.height - 200,
            color=arcade.color.WHITE,
            font_size=150,
            anchor_x="center"
        )


        self.score: List = []

    
    #what will happen if the view is showed.
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK_OLIVE)
        
        h = Score()
        self.score = h.load_score()
    
    #what will draw.
    def on_draw(self):

        #clear the screen before drawing new things to prevent overdrawing on last view.
        self.clear()

        #draw circle
        # arcade.draw_circle_filled(self.x_center , self.y_center, 15, arcade.color.RED)

        start_y = 230
        line_height = 100

        self.high_score_text.draw()

        self.score

        for index, item in enumerate(self.score):

            player_name, score = list(item.items())[0]
            row_y = self.height / 2 - (index * line_height)

            # Player Name
            arcade.draw_text(
                str(player_name),
                x=self.width / 2 - 350,
                y=row_y,
                color=arcade.color.CYAN,
                font_size=40,
                anchor_x= "center",
                anchor_y= "center",
            )

            # Score
            arcade.draw_text(
                str(score),
                x=self.width / 2 + 350,
                y=row_y,
                color=arcade.color.WHITE,
                font_size=40,
                anchor_x= "center",
                anchor_y= "center",
            )
            


#Game test view.
class Instuctions(arcade.View):

    #init with deafults.
    def __init__(self):
        super().__init__()

        self.x_center = self.width / 2
        self.y_center = self.height / 2
    
        self.instuctions_text = arcade.Text(
            text="Instructions here.",
            x = self.width / 2,
            y = self.height - 200,
            color=arcade.color.WHITE,
            font_size=150,
            anchor_x="center",
        )
    
    #what will happen if the view is showed.
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK_OLIVE)
    
    #what will draw.
    def on_draw(self):

        #clear the screen before drawing new things to prevent overdrawing on last view.
        self.clear()

        #draw circle
        arcade.draw_circle_filled(self.x_center , self.y_center, 15, arcade.color.RED)

        self.instuctions_text.draw()


  