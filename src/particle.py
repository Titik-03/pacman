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


class ShatterParticle:
    """Undertale-style soul shatter shard particle."""

    def __init__(self, x: float, y: float):
        self.x = x + random.uniform(-4, 4)
        self.y = y + random.uniform(-4, 4)
        speed = random.uniform(140, 360)
        angle = random.uniform(0, 2 * math.pi)
        # Upward bias + outward explosion velocity
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed * 0.7 + random.uniform(100, 240)
        self.gravity = 600.0
        self.w = random.uniform(6, 11)
        self.h = random.uniform(4, 9)
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-360, 360)
        self.lifetime = random.uniform(0.6, 1.0)
        self.max_lifetime = self.lifetime
        self.color = random.choice([
            (255, 230, 40),   # Pac-Man bright yellow
            (255, 255, 120),  # Light electric yellow
            (255, 255, 255),  # Pure white shard
            (255, 170, 50),   # Amber orange shard
            (255, 210, 30),   # Golden yellow
        ])

    def update(self, delta_time: float) -> bool:
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            return False
        self.vy -= self.gravity * delta_time
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.angle += self.spin * delta_time
        return True

    def draw(self):
        alpha = int(255 * max(0.0, self.lifetime / self.max_lifetime))
        arcade.draw_rect_filled(
            arcade.rect.XYWH(self.x, self.y, self.w, self.h),
            color=(*self.color, alpha),
            tilt_angle=self.angle
        )

class Floating_score:
    def __init__(self, x, y, text, color) -> None:
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.time = 0.8
        self.floating_speed = 50.0
    def update(self, delta_time):
        self.time -= delta_time
        self.y += self.floating_speed*delta_time
        return self.time>0
    def draw(self):
        alpha = int(255 * self.time / 0.8)
        r,g,b = self.color
        arcade.draw_text(
            self.text,
            self.x,
            self.y,
            color=(r,g,b,alpha),
            font_size=18,
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center"
        )