import arcade

class Coin:
    def __init__(self, x, y, is_powerup: bool = False):
        self.x = x
        self.y = y
        self.is_eaten = False
        self.is_powerup = is_powerup
        if self.is_powerup:
            self.radius = 8
            self.color = (255, 255, 255)
        else:
            self.radius = 3
            self.color = (255, 255, 0)

    def draw(self):
        if not self.is_eaten:
            arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)

