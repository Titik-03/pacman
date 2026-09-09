import arcade


# Game test view.
class Instuctions(arcade.View):
    """Instructions view displaying gameplay guidance."""

    # init with deafults.
    def __init__(self, main_menu: arcade.View, window: arcade.Window) -> None:
        """Initialize the instructions view layout and controls."""
        super().__init__()

        self.x_center = self.width / 2
        self.y_center = self.height / 2

        self.instuctions_text = arcade.Text(
            text="Instructions here.",
            x=self.width / 2,
            y=self.height - 200,
            color=arcade.color.WHITE,
            font_size=150,
            anchor_x="center",
        )

        self.main_menu = main_menu
        self.window = window

    # what will happen if the view is showed.

    def on_show_view(self) -> None:
        """Set up background when the view is displayed."""
        arcade.set_background_color(arcade.color.BLACK_OLIVE)

    # what will draw.
    def on_draw(self) -> None:
        """Render the instructions view."""

        # clear the screen before drawing new things to prevent overdrawing
        # on last view.
        self.clear()

        # draw circle
        arcade.draw_circle_filled(
            self.x_center, self.y_center, 15, arcade.color.RED)

        self.instuctions_text.draw()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle key press events to return to main menu."""
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu)
