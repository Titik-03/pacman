import arcade

class Coin:
    def __init__(self, x, y, is_powerup: bool = False):
        self.x = x
        self.y = y
        self.is_eaten = False
        self.is_powerup = is_powerup
        if self.is_powerup:
            self.radius = 9
            self.color = (255, 255, 220)
            self.glow_color = (255, 255, 255, 90)
        else:
            self.radius = 4
            self.color = (255, 200, 50)
            self.glow_color = None

    def draw(self):
        if not self.is_eaten:
            if self.is_powerup and self.glow_color:
                arcade.draw_circle_filled(self.x, self.y, self.radius + 4, self.glow_color)
            arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)

