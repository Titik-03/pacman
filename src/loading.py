import pathlib
import arcade
from src.game import GameWindow

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


class LoadingView(arcade.View):
    def __init__(self, window: arcade.Window, main_menu: arcade.View, seed: int, level: int = 1):
        super().__init__()
        self.window = window
        self.main_menu = main_menu
        self.level = level
        self.progress = 0.0
        self.loading_duration = 1.3  # duration in seconds for loading screen
        self.elapsed = 0.0
        self.game_view = None
        self.seed = seed

        # Catppuccin Mocha Color Palette
        self.MOCHA_BASE = (30, 30, 46)        # #1e1e2e
        self.MOCHA_SURFACE0 = (49, 50, 68)    # #313244
        self.MOCHA_TEXT = (205, 214, 244)     # #cdd6f4
        self.MOCHA_MAUVE = (203, 166, 247)    # #cba6f7
        self.MOCHA_LAVENDER = (180, 190, 254) # #b4befe
        self.MOCHA_YELLOW = (249, 226, 175)   # #f9e2af (Pac-Man)
        self.MOCHA_ROSEWATER = (245, 224, 220)# #f5e0dc (Dots)

        # Load Handjet font
        font_path = SCRIPT_DIR / "assets" / "Handjet" / "static" / "Handjet-Bold.ttf"
        if font_path.exists():
            arcade.load_font(str(font_path))

        self.title_text = arcade.Text(
            text=f"LOADING LEVEL {self.level}",
            x=self.width / 2,
            y=self.height / 2 + 100,
            color=self.MOCHA_MAUVE,
            font_size=72,
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center"
        )

        self.sub_text = arcade.Text(
            text="GET READY!",
            x=self.width / 2,
            y=self.height / 2 + 30,
            color=self.MOCHA_LAVENDER,
            font_size=36,
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center"
        )

    def on_show_view(self):
        arcade.set_background_color(self.MOCHA_BASE)
        # Instantiate GameWindow immediately so game assets/maze are ready

    def on_update(self, delta_time: float):
        self.elapsed += delta_time
        self.progress = min(1.0, self.elapsed / self.loading_duration)

        if self.elapsed >= self.loading_duration:
            self.window.show_view(GameWindow(self.main_menu, self.window, self.seed))

    def on_draw(self):
        self.clear()
        self.title_text.draw()
        self.sub_text.draw()

        # Loading Bar dimensions
        bar_w = int(550 * (self.width / 1920.0))
        bar_h = 24
        bar_x = self.width / 2 - bar_w / 2
        bar_y = self.height / 2 - 70

        # Draw outer track
        arcade.draw_rect_filled(
            arcade.LBWH(bar_x, bar_y, bar_w, bar_h),
            color=self.MOCHA_SURFACE0
        )
        arcade.draw_rect_outline(
            arcade.LBWH(bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4),
            color=self.MOCHA_MAUVE,
            border_width=2
        )

        # Draw filled progress bar
        fill_w = bar_w * self.progress
        if fill_w > 0:
            arcade.draw_rect_filled(
                arcade.LBWH(bar_x, bar_y, fill_w, bar_h),
                color=self.MOCHA_LAVENDER
            )

        # Draw dots ahead of Pac-Man along the loading bar
        dot_spacing = 35
        start_dot_x = bar_x + fill_w + 20
        end_dot_x = bar_x + bar_w - 10
        dot_x = start_dot_x
        while dot_x < end_dot_x:
            arcade.draw_circle_filled(dot_x, bar_y + bar_h / 2, 4, self.MOCHA_ROSEWATER)
            dot_x += dot_spacing

        # Draw animated champing Pac-Man at current progress position
        pac_x = bar_x + fill_w
        pac_y = bar_y + bar_h / 2
        mouth_angle = 35 * abs((self.elapsed * 8) % 2 - 1)
        arcade.draw_arc_filled(
            pac_x,
            pac_y,
            34,
            34,
            self.MOCHA_YELLOW,
            mouth_angle,
            360 - mouth_angle
        )

