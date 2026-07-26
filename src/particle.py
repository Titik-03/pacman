import arcade
import random
import math



class Particle:

    def __init__(self, width, height):

        self.screen_width = width
        self.screen_height = height

        self.x = random.randint(0, width)
        self.y = random.randint(0, height)

        self.radius = random.choice([1, 1, 1, 2, 2, 3, 4])

        self.speed = random.uniform(20, 60)

        self.alpha = random.randint(40, 120)

        self.color = random.choice([
            (255, 255, 255),
            (180, 240, 255),
            (100, 220, 255),
        ])

        self.drift = random.uniform(-8, 8)
        self.time = random.uniform(0, 6)

    def update(self, delta_time):

        self.time += delta_time
        self.x += self.drift * delta_time
        self.y += self.speed * delta_time

        if self.y > self.screen_height:
            self.y = -10
            self.x = random.randint(0, self.screen_width)

    def draw(self):

        alpha = self.alpha + math.sin(self.time * 3) * 30
        alpha = max(20, min(180, int(alpha)))

        arcade.draw_circle_filled(
            self.x,
            self.y,
            self.radius,
            (*self.color, alpha)
        )
