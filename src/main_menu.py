from arcade import application
from arcade import window_commands
from arcade.gui import widgets
import arcade
import arcade.gui
from src.instructions import Instuctions
from src.score import HighScore, Score
from src.game import GameWindow
from src.banner import Banner
from src.menu_item import MenuItem
from src.particle import Particle

# Main menu view.
class MainMenu(arcade.View):

    def __init__(self, window):

        super().__init__()

        # self.x_center = window.width / 2
        # self.y_center = window.height / 2

        arcade.load_font("src/assets/Handjet/static/Handjet-Regular.ttf")
        arcade.load_font("src/assets/Handjet/static/Handjet-Bold.ttf")

        # Init the game view
        self.game_view = GameWindow(self, window)
        self.high_score_view = HighScore(self, window)
        self.instuctions_view = Instuctions(self, window)
        self.top_banner = Banner(1300, 1300)
        self.bottom_banner = Banner(1300, -1600)
        self.score_manager = Score()
        self.window = window

        self.scores = []

        self.background = arcade.load_texture("src/assets/Desktop - 1.png")
        self.instructions_image = arcade.load_texture("src/assets/Frame 1.png")
        self.title_text = arcade.Text(
            text="PAC-MAN",
            x=5,
            y=window.height * 0.8,
            color=arcade.color.WHITE,
            font_size=160,
            font_name="Handjet",
            bold=True,
            # anchor_x="right"
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
                    120,
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

        if self.hovered != self.last_hovered:
            if self.hovered == 1:
                self.top_banner.move_to(1000, 600)
                self.bottom_banner.move_to(1300, -1600)
            elif self.hovered == 2:
                self.top_banner.move_to(1300, 1300)
                self.bottom_banner.move_to(570, -600)
            elif self.hovered == 3:
                self.top_banner.move_to(1000, 600)
                self.bottom_banner.move_to(570, -600)
            else:
                self.top_banner.move_to(1300, 1300)
                self.bottom_banner.move_to(1300, -1600)

            if self.hovered != -1:
                arcade.play_sound(self.hover_sound)

            self.last_hovered = self.hovered

        self.top_banner.update()
        self.bottom_banner.update()


    def on_key_press(self, key, modifiers):

        if key == arcade.key.UP:
            self.menu_items[self.last_hovered].hovered = False
            if self.hovered == -1:
                self.hovered = 0

            else:
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
                self.game_view = GameWindow(self, self.window)
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
            self.game_view = GameWindow(self, self.window)
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
        self.title_text.x = 5
        self.title_text.y = height * 0.8

    # What will happen if the view is shown.
    def on_show_view(self):

        # Setting background color.
        self.scores = self.score_manager.load_score()

    def draw_leaderboard(self):

        top_y = self.top_banner.y + 480
        margin_x = 130
        width = 700
        row_height = 50

        for i, item in enumerate(self.scores[:10]):

            name, score = list(item.items())[0]
            row_y = top_y - (i * row_height)

            edge_x = (self.top_banner.x - 200) + (row_y - self.top_banner.y) * 0.35
            row_x = edge_x + margin_x

            if i == 0:
                rank_color = (255, 215, 0)      # Gold
            elif i == 1:
                rank_color = (210, 220, 235)    # Silver
            elif i == 2:
                rank_color = (225, 145, 65)     # Bronze
            else:
                rank_color = (230, 230, 235)    # Crisp White

            arcade.draw_text(
                f"{i + 1:02d}.",
                row_x,
                row_y,
                rank_color,
                45,
                font_name="Handjet",
                bold=True,
            )

            arcade.draw_text(
                str(name).upper(),
                row_x + 65,
                row_y,
                arcade.color.WHITE,
                45,
                font_name="Handjet",
                bold=True,
            )

            arcade.draw_text(
                f"{score}",
                row_x + width,
                row_y,
                (0, 240, 255),
                45,
                font_name="Handjet",
                bold=True,
                anchor_x="right"
            )

    def draw_instructions(self):

        left = self.bottom_banner.x + 190
        bottom = self.bottom_banner.y + 600
        width = 1150
        height = 400

        arcade.draw_texture_rect(
            self.instructions_image,
            arcade.LBWH(
                left,
                bottom,
                width,
                height
            )
        )


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

        # self.draw_maze_background()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(
                0,
                0,
                self.window.width,
                self.window.height,
            ),
        )

        for particle in self.particles:
            particle.draw()

        self.top_banner.draw()
        self.bottom_banner.draw()

        self.draw_leaderboard()
        self.draw_instructions()

        for item in self.menu_items:
            item.draw()

        self.title_text.draw()
