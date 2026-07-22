from typing import List, Dict
import json
import arcade
import arcade.gui


class HighScore(arcade.View):

    #init with deafults.
    def __init__(self, main_menu: arcade.View, window: arcade.Window):
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

        self.main_menu = main_menu
        self.window = window

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

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu)



class Score:

    def __init__(self) -> List[Dict]:

        self.score: List[Dict] = []
    
    def load_score(self):
        try:
            with open("src/outputs/high_score.json", "r") as fp:
                self.score = json.load(fp)
            print(self.score)

        except Exception as e:
            print(e)
        return self.score

    def write_score(self, new_data: Dict) -> List[Dict]:
        existing_data: List = []
        try:
            with open("src/outputs/high_score.json", "r") as fp:
                existing_data = json.load(fp)
            
            existing_data.append(new_data)

            with open("src/outputs/high_score.json", "w") as fp:
                json.dump(existing_data, fp, indent=4)

        except Exception as e:
            print(e)
        
        return existing_data
