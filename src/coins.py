import math
import time
import arcade


class Coin:
    def __init__(self, x, y, is_powerup: bool = False):
        self.x = x
        self.y = y
        self.is_eaten = False
        self.is_powerup = is_powerup
        if self.is_powerup:
            self.radius = 9
            self.color = (245, 224, 220)  # Catppuccin Mocha Rosewater
            self.glow_color = (245, 224, 220, 100)
        else:
            self.radius = 4
            self.color = (249, 226, 175)  # Catppuccin Mocha Yellow
            self.glow_color = None

    def draw(self):
        if self.is_eaten:
            return

        hover = math.sin(time.time() * 3.5 + (self.x + self.y) * 0.03)
        draw_y = self.y + hover * (3.0 if self.is_powerup else 1.5)

        if self.is_powerup and self.glow_color:
            arcade.draw_circle_filled(
                self.x, draw_y, self.radius + 4, self.glow_color
            )
        arcade.draw_circle_filled(self.x, draw_y, self.radius, self.color)
