import arcade

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
SCREEN_TITLE = "Arcade Leaderboard"

class LeaderboardView(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # Your input data
        self.leaderboard_data = [{"name": 122}, {"name2": 211}]

    def on_draw(self):
        self.clear()

        # 1. Draw Title
        arcade.draw_text(
            "LEADERBOARD",
            x=SCREEN_WIDTH / 2,
            y=330,
            color=arcade.color.GOLD,
            font_size=24,
            bold=True,
            anchor_x="center"
        )

        # 2. Draw Table Headers
        arcade.draw_text("Player", x=150, y=280, color=arcade.color.WHITE, font_size=16, bold=True)
        arcade.draw_text("Score", x=400, y=280, color=arcade.color.WHITE, font_size=16, bold=True)
        
        # Divider line
        arcade.draw_line(150, 270, 450, 270, arcade.color.LIGHT_GRAY, 2)

        # 3. Draw Each Row
        start_y = 230
        line_height = 40

        for index, item in enumerate(self.leaderboard_data):
            # Dynamic extraction of key & value
            player_name, score = list(item.items())[0]
            row_y = start_y - (index * line_height)

            # Player Name
            arcade.draw_text(
                str(player_name),
                x=150,
                y=row_y,
                color=arcade.color.CYAN,
                font_size=14
            )

            # Score
            arcade.draw_text(
                str(score),
                x=400,
                y=row_y,
                color=arcade.color.WHITE,
                font_size=14
            )

def main():
    window = LeaderboardView()
    arcade.run()

if __name__ == "__main__":
    main()