import arcade  # Import Arcade for drawing the particle.
import random  # Import random for generating particle properties.
import math  # Import math for the sine wave used in alpha animation.



class Particle:

    def __init__(self, width, height):

        self.screen_width = width  # Store the width of the screen.
        self.screen_height = height  # Store the height of the screen.

        self.x = random.randint(0, width)  # Pick a random starting x position.
        self.y = random.randint(0, height)  # Pick a random starting y position.

        self.radius = random.choice([1, 1, 7, 7, 2, 3, 4, 6, 6, 6])  # Pick a small random radius.

        self.speed = random.uniform(20, 60)  # Pick a random upward speed.

        self.alpha = random.randint(40, 120)  # Pick a base transparency value.

        self.color = random.choice([  # Choose a color for the particle.
            (255, 255, 255),  # Use white as one possible color.
            (180, 240, 255),  # Use a pale blue as one possible color.
            (100, 220, 255),  # Use a brighter blue as one possible color.
            (255, 255, 0),  # Use yellow as one possible color.
            (255, 255, 0),  # Repeat yellow to make it more likely.
            (255, 255, 0),  # Repeat yellow again to weight the choice.
            (255, 255, 0)  # Repeat yellow a final time to weight the choice.
        ])

        self.drift = random.uniform(-8, 8)  # Pick a random horizontal drift.
        self.time = random.uniform(0, 6)  # Start the animation clock at a random point.

    def update(self, delta_time):

        self.time += delta_time  # Advance the internal animation timer.
        self.x += self.drift * delta_time  # Move horizontally based on drift.
        self.y += self.speed * delta_time  # Move upward based on speed.

        if self.y > self.screen_height:  # Check whether the particle moved off the top.
            self.y = -10  # Reset the particle just below the bottom edge.
            self.x = random.randint(0, self.screen_width)  # Give it a new random x position.

    def draw(self):

        alpha = self.alpha + math.sin(self.time * 3) * 30  # Add a pulsing alpha variation.
        alpha = max(20, min(180, int(alpha)))  # Clamp alpha to a visible range.

        arcade.draw_circle_filled(  # Draw the particle as a filled circle.
            self.x,  # Use the current x position.
            self.y,  # Use the current y position.
            self.radius,  # Use the chosen radius.
            (*self.color, alpha)  # Combine RGB color with the computed alpha.
        )
