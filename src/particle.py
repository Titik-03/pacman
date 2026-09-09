import math  # Import math for the sine wave used in alpha animation.
import random  # Import random for generating particle properties.
import arcade  # Import Arcade for drawing the particle.
from arcade.types import Color


class Particle:

    def __init__(self, width: int, height: int) -> None:

        self.screen_width = width
        self.screen_height = height

        self.x: float = float(random.randint(0, width))
        self.y: float = float(random.randint(0, height))

        # Pick a small random radius.
        self.radius = random.choice([1, 1, 7, 7, 2, 3, 4, 6, 6, 6])

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
        # Start the animation clock at a random point.
        self.time = random.uniform(0, 6)

    def update(self, delta_time: float) -> None:

        self.time += delta_time  # Advance the internal animation timer.
        self.x += self.drift * delta_time  # Move horizontally based on drift.
        self.y += self.speed * delta_time  # Move upward based on speed.

        # Check whether the particle moved off the top.
        if self.y > self.screen_height:
            self.y = -10  # Reset the particle just below the bottom edge.
            # Give it a new random x position.
            self.x = random.randint(0, self.screen_width)

    def draw(self) -> None:

        # Add a pulsing alpha variation.
        alpha = self.alpha + math.sin(self.time * 3) * 30
        # Clamp alpha to a visible range.
        alpha = max(20, min(180, int(alpha)))

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

    def draw(self) -> None:
        alpha = int(255 * max(0.0, self.lifetime / self.max_lifetime))
        arcade.draw_rect_filled(
            arcade.rect.XYWH(self.x, self.y, self.w, self.h),
            color=(*self.color, alpha),
            tilt_angle=self.angle
        )


class Floating_score:
    def __init__(
        self,
        x: float,
        y: float,
        text: str,
        color: tuple[int, int, int],
    ) -> None:
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.time = 0.8
        self.floating_speed = 50.0

    def update(self, delta_time: float) -> bool:
        self.time -= delta_time
        self.y += self.floating_speed*delta_time
        return self.time > 0

    def draw(self) -> None:
        alpha = int(255 * self.time / 0.8)
        r, g, b = self.color
        arcade.draw_text(
            self.text,
            self.x,
            self.y,
            color=(r, g, b, alpha),
            font_size=18,
            font_name="Handjet",
            bold=True,
            anchor_x="center",
            anchor_y="center"
        )


class TrailParticle:
    def __init__(
        self,
        x: float,
        y: float,
        texture: arcade.Texture,
        angle: float,
        width: float,
        height: float,
        color: tuple[int, int, int] | Color = (203, 166, 247),
        lifetime: float = 0.22,
    ):
        self.x = x
        self.y = y
        self.texture = texture
        self.angle = angle
        self.width = width
        self.height = height
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self, delta_time: float) -> bool:
        self.lifetime -= delta_time
        return self.lifetime > 0

    def draw(self) -> None:
        alpha = int(140 * max(0.0, self.lifetime / self.max_lifetime))

        tint_color = Color(int(self.color[0]), int(
            self.color[1]), int(self.color[2]), alpha)

        arcade.draw_texture_rect(
            self.texture,
            arcade.rect.XYWH(self.x, self.y, self.width, self.height),
            angle=self.angle,
            color=tint_color
        )


class Shockwave:
    def __init__(
        self, x: float, y: float, color: tuple[int, int, int]
    ) -> None:
        self.x = x
        self.y = y
        self.max_radius = 300.0
        self.current_radius = 0.0
        self.duration = 0.6
        self.lifetime = self.duration
        self.color = color

    def update(self, delta_time: float) -> bool:
        self.lifetime -= delta_time
        return self.lifetime > 0

    def draw(self) -> None:
        r, g, b = self.color
        progress = 1.0 - (self.lifetime / self.duration)
        radius = self.max_radius * progress
        alpha = int(230 * (1.0 - progress))
        arcade.draw_circle_outline(
            self.x,
            self.y,
            max(1.0, radius),
            (r, g, b, alpha),
            3
        )


class CoinSparkle:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.vx = random.uniform(-60, 60)
        self.vy = random.uniform(-60, 60)
        self.lifetime = 0.25  # Total duration in seconds
        self.color = random.choice(
            [arcade.color.YELLOW, arcade.color.WHITE, arcade.color.GOLD])

    def update(self, delta_time: float) -> bool:
        self.lifetime -= delta_time
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        return self.lifetime > 0

    def draw(self) -> None:
        alpha = int(255 * (self.lifetime / 0.25))
        arcade.draw_point(
            self.x,
            self.y,
            Color(self.color[0], self.color[1], self.color[2], max(0, alpha)),
            size=4
        )
