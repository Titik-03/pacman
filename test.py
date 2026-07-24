import arcade
import arcade.gui

class GameOverView(arcade.View):
    def __init__(self, score: int):
        super().__init__()
        self.score = score
        
        # 1. Initialize UIManager
        self.manager = arcade.gui.UIManager()
        
        # 2. Build layout once inside __init__
        layout = arcade.gui.UIAnchorLayout()
        box = arcade.gui.UIBoxLayout(space_between=15)
        
        # Score Label
        score_label = arcade.gui.UILabel(
            text=f"GAME OVER! Score: {self.score}", 
            font_size=20,
            text_color=arcade.color.YELLOW
        )
        box.add(score_label)
        
        # Input Text Field
        self.input_field = arcade.gui.UIInputText(
            width=250, 
            height=40, 
            font_size=16
        )
        box.add(self.input_field)
        
        # Submit Button
        submit_btn = arcade.gui.UIFlatButton(text="Submit Highscore", width=200)
        box.add(submit_btn)
        
        # Bind button click event
        @submit_btn.event("on_click")
        def on_click_submit(event):
            player_name = self.input_field.text.strip()
            if player_name:
                self.save_score(player_name, self.score)

        layout.add(box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(layout)
        
    def on_show_view(self):
        # Simply enable the manager when entering the view
        self.manager.enable()

    def on_hide_view(self):
        # Disable the manager when leaving the view
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def save_score(self, name: str, score: int):
        print(f"Saved score for {name}: {score}")

# Create window, show view, and run the main game loop!
window = arcade.Window(800, 600, "Pac-Man Highscore")
g = GameOverView(999)
window.show_view(g)

arcade.run()  # <--- Starts the game loop