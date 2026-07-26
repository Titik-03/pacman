import arcade
import arcade.gui
from instructions import Instuctions
from score import HighScore, Score
from game import Game
from banner import Banner
from menu_item import MenuItem
from particle import Particle

# Main menu view.
class MainMenu(arcade.View):

    def __init__(self, window):

        super().__init__()

        # self.x_center = window.width / 2
        # self.y_center = window.height / 2

        # Init the game view
        self.game_view = Game(self, window)
        self.high_score_view = HighScore(self, window)
        self.instuctions_view = Instuctions(self, window)
        self.window = window
        self.banner = Banner()
        self.score_manager = Score()

        self.scores = []

        self.title_text = arcade.Text(
            text="PAC-MAN",
            x=window.width * 0.2,
            y=window.height * 0.8,
            color=arcade.color.WHITE,
            font_size=100,
            # bold=True,
            anchor_x="center"
        )

        self.hovered = -1
        self.last_hovered = -1

        self.menu_items = []

        labels = [
            "START GAME",
            "HIGH SCORE",
            "INSTRUCTIONS",
            "QUIT GAME"
        ]

        start_y = 650

        for i, label in enumerate(labels):

            self.menu_items.append(

                MenuItem(
                    label,
                    220,
                    start_y - i * 90
                )

            )

        self.particles = []

        for _ in range(35):
            self.particles.append(
                Particle(
                    window.width,
                    window.height
                )
            )

        self.hover_sound = arcade.load_sound("src/assets/COMSE_00.VAG.wav")



    def on_update(self, delta_time):

        for particle in self.particles:
            particle.update(delta_time)

        for item in self.menu_items:
            item.update()

        if self.hovered != -1:
            item = self.menu_items[self.hovered]

            self.banner.move_to(
                180,
                item.text.y - 10,
                item.text.content_width + 80
            )
        else:
            self.banner.move_to(
                -500,
                self.banner.y,
                self.banner.width
            )
        
        if self.hovered != self.last_hovered:
            if self.hovered != -1:
                arcade.play_sound(self.hover_sound)


            self.last_hovered = self.hovered

        self.banner.update()


    def on_key_press(self, key, modifiers):

        if key == arcade.key.UP:
            self.menu_items[self.last_hovered].hovered = False
            self.hovered -= 1
            self.hovered %= len(self.menu_items)
            self.menu_items[self.hovered].hovered = True

        if key == arcade.key.DOWN:
            self.menu_items[self.last_hovered].hovered = False
            self.hovered += 1
            self.hovered %= len(self.menu_items)
            self.menu_items[self.hovered].hovered = True


        if key == arcade.key.ENTER:
            if self.hovered == 0:
                self.window.show_view(self.game_view)

            elif self.hovered == 1:
                self.window.show_view(self.high_score_view)
    
            elif self.hovered == 2:
                self.window.show_view(self.instuctions_view)
    
            elif self.hovered == 3:
                arcade.exit()


    def on_mouse_motion(self, x, y, dx, dy):

        self.hovered = -1

        for index, item in enumerate(self.menu_items):

            item.hovered = item.contains(x, y)

            if item.hovered:
                self.hovered = index
                break
        


    def on_mouse_press(self, x, y, button, modifiers):

        if self.hovered == -1:
            return

        if self.hovered == 0:
            self.window.show_view(self.game_view)


        elif self.hovered == 1:
            self.window.show_view(self.high_score_view)

        elif self.hovered == 2:
            self.window.show_view(self.instuctions_view)

        elif self.hovered == 3:
            arcade.exit()

    # Update whenever resizing the screen. 
    def on_resize(self, width: int, height: int):

        super().on_resize(width, height)
        self.title_text.x = width * 0.2
        self.title_text.y = height * 0.8

    # What will happen if the view is shown.
    def on_show_view(self):

        # Setting background color.
        arcade.set_background_color((8, 12, 28))

        self.scores = self.score_manager.load_score()

    def draw_leaderboard(self):

        x = self.window.width * 0.68
        y = self.window.height * 0.66

        width = 500
        height = 460

        arcade.draw_lrbt_rectangle_filled(
            x + 8,
            x + width + 8,
            y - height - 8,
            y - 8,
            (0, 0, 0, 100)
        )

        arcade.draw_lrbt_rectangle_outline(
            x,
            x + width,
            y - height,
            y,
            (0, 240, 255),
            border_width=2
        )

        arcade.draw_text(
            "TOP PLAYERS",
            x + width / 2,
            y - 40,
            (255, 255, 0),
            28,
            bold=True,
            anchor_x="center"
        )

        arcade.draw_line(
            x + 25,
            y - 75,
            x + width - 25,
            y - 75,
            (0,240,255),
            line_width=2
        )

        row_y = y - 120

        for i, item in enumerate(self.scores[:10]):

            name, score = list(item.items())[0]

            if i == 0:
                rank_color = arcade.color.GOLD
            elif i == 1:
                rank_color = arcade.color.SILVER
            elif i == 2:
                rank_color = (205, 127, 50)   # bronze
            else:
                rank_color = arcade.color.WHITE

            arcade.draw_text(
                f"{i + 1}.",
                x + 30,
                row_y,
                rank_color,
                22,
                bold=True,
            )

            arcade.draw_text(
                name,
                x + 70,
                row_y,
                arcade.color.WHITE,
                22,
            )

            arcade.draw_text(
                str(score),
                x + width - 30,
                row_y,
                arcade.color.CYAN,
                22,
                anchor_x="right"
            )

            row_y -= 35
        

    def draw_maze_background(self):

        color = (0, 180, 255, 30)

        self.wall_h(900, 1200, 800, color)
        self.wall_v(1200, 600, 800, color)

        self.wall_h(700, 950, 500, color)
        self.wall_v(700, 300, 500, color)

    def wall_h(self, x1, x2, y, color):
        arcade.draw_line(x1, y, x2, y, color, 6)

    def wall_v(self, x, y1, y2, color):
        arcade.draw_line(x, y1, x, y2, color, 6)


    # What will draw.
    def on_draw(self):

        self.clear()

        w = self.window.width
        h = self.window.height

        self.draw_maze_background()

        self.draw_leaderboard()

        for particle in self.particles:
            particle.draw()

        self.banner.draw()

        for item in self.menu_items:
            item.draw()

        self.title_text.draw()

window = arcade.Window(1920, 1080, "Pac-man", resizable=True, fullscreen=True)

main_menu = MainMenu(window)

window.show_view(main_menu)

arcade.run()
