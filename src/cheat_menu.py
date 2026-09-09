import arcade
import arcade.gui


class CheatMenu(arcade.View):
    """Pause view overlay for cheats."""

    def __init__(self, game: arcade.View) -> None:
        """Initialize the cheat menu with reference to active game view."""
        super().__init__()

        self.game = game

    def on_draw(self) -> None:
        """Render the cheat menu overlay."""
        self.clear()

        arcade.draw_text(
            "PAUSED",
            self.window.width / 2,
            self.window.height / 2 + 50,
            arcade.color.WHITE,
            40,
            anchor_x="center",
        )

        arcade.draw_text(
            "Press ESC to resume",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.GRAY,
            20,
            anchor_x="center",
        )

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle key press events to resume game."""
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(self.game)


# window = arcade.Window(
#     1920, 1080, "Pac-man", resizable=True, fullscreen=True
# )

# p = PauseMenu()


# window.show_view(p)

# arcade.run()
