import arcade
import arcade.gui

from src.instructions import Instuctions
from src.score import HighScore, Score
from src.loading import LoadingView
from src.banner import Banner
from src.menu_item import MenuItem
from src.particle import Particle
from src.sound_manager import SoundManager
from src.levels import ConfigParser


# Main menu view.
class MainMenu(arcade.View):
    def __init__(
        self,
        window: arcade.Window,
        config_parser: ConfigParser | None = None,
    ) -> None:
        super().__init__()
        arcade.load_font("src/assets/Handjet/static/Handjet-Regular.ttf")
        arcade.load_font("src/assets/Handjet/static/Handjet-Bold.ttf")

        self.config_parser = config_parser or ConfigParser()
        self.high_score_view = HighScore(self, window)
        self.instuctions_view = Instuctions(self, window)
        self.top_banner = Banner(window.width + 300, window.height + 300)
        self.bottom_banner = Banner(window.width + 300, -window.height - 500)

        self.score_manager = Score(
            filepath=self.config_parser.highscore_filename
        )
        self.window = window
        self.scores = []
        self.background = arcade.load_texture("src/assets/menu.png")
        self.instructions_image = arcade.load_texture("src/assets/Frame 1.png")
        self.title_text = arcade.Text(
            text="PAC-MAN",
            x=5,
            y=window.height * 0.8,
            color=arcade.color.WHITE,
            font_size=160,
            font_name="Handjet",
            bold=True,
        )

        self.hovered = -1
        self.last_hovered = -1
        self.show_instructions = False
        self.show_highscore = False
        # self.seed = 42

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

    def on_update(self, delta_time):
        for particle in self.particles:
            particle.update(delta_time)
        for item in self.menu_items:
            item.update()

        if self.show_instructions:
            self.bottom_banner.move_to(-400, -200)
            self.bottom_banner.target_height = self.window.height + 400
            self.top_banner.move_to(
                self.window.width + 300, self.window.height + 300)
        elif self.show_highscore:
            self.top_banner.move_to(-400, -200)
            self.top_banner.target_height = self.window.height + 400
            self.bottom_banner.move_to(
                self.window.width + 300, -self.window.height - 500)
        else:
            self.bottom_banner.target_height = 1000
            if self.hovered != self.last_hovered:
                if self.hovered == 1:
                    self.top_banner.move_to(
                        self.window.width - 920, self.window.height - 550)
                    self.bottom_banner.move_to(
                        self.window.width + 300, -self.window.height - 500)
                elif self.hovered == 2:
                    self.top_banner.move_to(
                        self.window.width + 300, self.window.height + 300)
                    self.bottom_banner.move_to(570, -600)
                elif self.hovered == 3:
                    self.top_banner.move_to(
                        self.window.width - 920, self.window.height - 550)
                    self.bottom_banner.move_to(570, -600)
                else:
                    self.top_banner.move_to(
                        self.window.width + 300, self.window.height + 300)
                    self.bottom_banner.move_to(
                        self.window.width + 300, -self.window.height - 500)

                if self.hovered != -1:
                    SoundManager.get().play_sfx("menu_hover")
                self.last_hovered = self.hovered

        self.top_banner.update()
        self.bottom_banner.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            for item in self.menu_items:
                item.hovered = False
            if self.show_instructions or self.show_highscore:
                self.show_instructions = False
                self.show_highscore = False
                self.hovered = -1
                self.last_hovered = 999
                return
        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
        if key == arcade.key.UP:
            for item in self.menu_items:
                item.hovered = False
            self.menu_items[self.last_hovered].hovered = False
            if self.hovered == -1:
                self.hovered = 0
            else:
                self.hovered -= 1
                self.hovered %= len(self.menu_items)
            self.menu_items[self.hovered].hovered = True

        if key == arcade.key.DOWN:
            for item in self.menu_items:
                item.hovered = False
            self.menu_items[self.last_hovered].hovered = False
            self.hovered += 1
            self.hovered %= len(self.menu_items)
            self.menu_items[self.hovered].hovered = True

        if key == arcade.key.ENTER:
            if self.hovered != -1:
                SoundManager.get().play_sfx("menu_select")
            if self.hovered == 0:
                loading_view = LoadingView(self.window, self, level=1)
                self.window.show_view(loading_view)

            elif self.hovered == 1:
                self.scores = self.score_manager.load_score()
                self.show_highscore = True
                self.last_hovered = -1
            elif self.hovered == 2:
                # Trigger instructions banner expansion instead of showing view
                self.show_instructions = True
                self.last_hovered = -1
            elif self.hovered == 3:
                arcade.exit()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.show_instructions or self.show_highscore:
            return

        self.hovered = -1
        for index, item in enumerate(self.menu_items):
            item.hovered = item.contains(x, y)
            if item.hovered:
                self.hovered = index
                break

    def on_mouse_press(self, x, y, button, modifiers):
        # Click anywhere to close instructions
        if self.show_instructions or self.show_highscore:
            for item in self.menu_items:
                item.hovered = False
            self.show_instructions = False
            self.show_highscore = False
            self.hovered = -1
            self.last_hovered = 999
            SoundManager.get().play_sfx("menu_select")

        if self.hovered == -1:
            return
        SoundManager.get().play_sfx("menu_select")
        if self.hovered == 0:
            loading_view = LoadingView(self.window, self, level=1)
            self.window.show_view(loading_view)

        elif self.hovered == 1:
            self.scores = self.score_manager.load_score()
            self.show_highscore = True
            self.last_hovered = -1
        elif self.hovered == 2:
            self.show_instructions = True
            self.last_hovered = -1
        elif self.hovered == 3:
            arcade.exit()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.title_text.x = 5
        self.title_text.y = height * 0.8

    def on_show_view(self):
        SoundManager.get().play_music("menu", loop=True)
        self.scores = self.score_manager.load_score()

    def draw_leaderboard(self):
        width = 700
        row_height = 50

        # Interpolation Logic
        if self.show_highscore:
            for item in self.menu_items:
                item.hovered = False
            # Final destination for the expanded leaderboard
            target_left = (self.window.width / 2 - width / 2) + 150
            target_top = self.window.height / 2 + 200

            # Calculate progress based on banner movement
            start_y = self.window.height - 550
            progress = (start_y - self.top_banner.y) / (start_y - (-200))
            progress = max(0, min(1, progress))

            # Start position matching the preview layout
            current_top_y = self.top_banner.y + 480
            current_edge_x = (self.top_banner.x - 200) + \
                (current_top_y - self.top_banner.y) * 0.35

            left = (current_edge_x + 130) * \
                (1 - progress) + target_left * progress
            top_y = current_top_y * (1 - progress) + target_top * progress

            # Draw exit prompt & Title when expanded
            arcade.draw_text(
                "Press ESC or Click anywhere to return",
                self.window.width / 2,
                70,
                arcade.color.WHITE,
                28,
                font_name="Handjet",
                anchor_x="center",
            )

            arcade.draw_text(
                "HIGH SCORES",
                left + width / 2,
                top_y + 80,
                arcade.color.CYAN,
                60,
                font_name="Handjet",
                bold=True,
                anchor_x="center",
            )
        else:
            top_y = self.top_banner.y + 480
            edge_x = (self.top_banner.x - 200) + \
                (top_y - self.top_banner.y) * 0.35
            left = edge_x + 130

        # Draw the actual scores
        for i, item in enumerate(self.scores[:10]):
            name = item["name"]
            score = item["score"]
            row_y = top_y - (i * row_height)
            row_x = left

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
                row_x, row_y, rank_color, 45, font_name="Handjet", bold=True,
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
                anchor_x="right",
            )

    def draw_instructions(self):
        width = 1150
        height = 400

        if self.show_instructions:
            target_left = self.window.width / 2 - width / 2 + 200
            target_bottom = self.window.height / 2 - height / 2

            progress = (self.bottom_banner.y - (-600)) / 400
            progress = max(0, min(1, progress))

            left = (self.bottom_banner.x + 190) * \
                (1 - progress) + target_left * progress
            bottom = (self.bottom_banner.y + 600) * \
                (1 - progress) + target_bottom * progress

            # Show "Close" prompt when expanded
            arcade.draw_text("Press ESC or Click anywhere to return",
                             self.window.width / 2,
                             70,
                             arcade.color.WHITE,
                             28,
                             font_name="Handjet",
                             anchor_x="center")
        else:
            left = self.bottom_banner.x + 190
            bottom = self.bottom_banner.y + 600

        arcade.draw_texture_rect(
            self.instructions_image,
            arcade.LBWH(
                left,
                bottom,
                width,
                height
            )
        )

    def new_game(self, seed: int = 42):
        loading_view = LoadingView(self.window, self, seed, level=1)
        self.window.show_view(loading_view)

    def on_draw(self):
        self.clear()

        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(
                0,
                0,
                self.window.width,
                self.window.height,
            ),
        )

        self.top_banner.draw()
        self.bottom_banner.draw()

        self.draw_leaderboard()
        self.draw_instructions()

        for particle in self.particles:
            particle.draw()

        for item in self.menu_items:
            item.draw()

        self.title_text.draw()
