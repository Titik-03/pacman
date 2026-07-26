import arcade


class Banner:

    def __init__(self):

        self.x = -450
        self.y = 650

        # self.width = 420
        self.height = 55
        self.width = 0
        self.target_width = 0

        self.target_x = -500
        self.target_y = 0

        self.color = (240, 40, 40)

        # self.visible = False

    def move_to(self, x, y, width):
            self.target_x = x
            self.target_y = y
            self.target_width = width

    def update(self):

        self.width += (self.target_width - self.width) * 0.15
        self.x += (self.target_x - self.x) * 0.15
        self.y += (self.target_y - self.y) * 0.20

    def draw(self):

        shadow = [
            (self.x + 8, self.y - 8),
            (self.x + self.width + 8, self.y - 8),
            (self.x + self.width - 40 + 8, self.y + self.height - 8),
            (self.x - 40 + 8, self.y + self.height - 8),
        ]

        arcade.draw_polygon_filled(
            shadow,
            (0,0,0,120)
        )

        points = [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width - 40, self.y + self.height),
            (self.x - 40, self.y + self.height),
        ]

        arcade.draw_polygon_filled(points, self.color)

        arcade.draw_polygon_outline(
            points,
            arcade.color.WHITE,
            line_width=2
        )

        accent = [
            (self.x + 20, self.y + self.height - 12),
            (self.x + 120, self.y + self.height - 12),
            (self.x + 100, self.y + self.height - 4),
            (self.x, self.y + self.height - 4),
        ]

        arcade.draw_polygon_filled(
            accent,
            arcade.color.WHITE
        )
