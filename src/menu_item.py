import arcade
import math


class MenuItem:

    def __init__(self, label: str, x: float, y: float):

        self.base_x = x
        self.base_y = y

        self.offset = 0

        self.font_size = 32

        self.arrow_offset = -20
        self.time = 0

        self.text = arcade.Text(
            label,
            x,
            y,
            arcade.color.WHITE,
            32,
            bold=True,
        )

        self.hovered = False

        self.arrow = [
            (self.text.x + self.arrow_offset, self.text.y + 8),
            (self.text.x + self.arrow_offset + 18, self.text.y + 18),
            (self.text.x + self.arrow_offset, self.text.y + 28),
        ]

    def update(self):

        self.time += 1 / 60

        target = 0 if self.hovered else -20

        self.arrow_offset += (target - self.arrow_offset) * 0.20

    def draw(self):

        arrow_x = self.text.x - 20 + self.arrow_offset
        arrow_y = self.text.y + math.sin(self.time * 8) * 2

        arrow = [
            (arrow_x, arrow_y + 8),
            (arrow_x + 18, arrow_y + 18),
            (arrow_x, arrow_y + 28),
        ]

        if self.hovered:
            arcade.draw_polygon_filled(
                arrow,
                arcade.color.WHITE
            )

        self.text.color = (
            arcade.color.YELLOW
            if self.hovered
            else arcade.color.WHITE
        )

        self.text.draw()

    def contains(self, x, y):

        return (
            self.text.x <= x <= self.text.x + self.text.content_width
            and
            self.text.y <= y <= self.text.y + self.text.content_height
        )


