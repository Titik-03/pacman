import arcade  # Import Arcade for text and shape drawing.
import math  # Import math for the sine-based hover animation.


class MenuItem:

    def __init__(self, label: str, x: float, y: float) -> None:

        self.offset = 0  # Keep a generic offset value for layout or animation.

        self.arrow_offset: float = -20.0  # Start the arrow slightly left.
        self.time: float = 0.0  # Track elapsed time for animation.

        self.text = arcade.Text(  # Create the text object for the menu item.
            label,  # Use the provided label string.
            x,  # Use the provided x coordinate.
            y,  # Use the provided y coordinate.
            arcade.color.WHITE,  # Start with white text.
            50,  # Use a 32-point font size.
            font_name="Handjet",
            bold=True,  # Draw the label in bold.
        )

        self.hovered = False  # Track whether the mouse is over the item.

        self.arrow = [  # Build the initial arrow polygon points.
            # Set the top point.
            (self.text.x + self.arrow_offset, self.text.y + 8),
            # Set the tip point.
            (self.text.x + self.arrow_offset + 18, self.text.y + 18),
            # Set the bottom point.
            (self.text.x + self.arrow_offset, self.text.y + 28),
        ]

    def update(self) -> None:

        self.time += 1 / 60  # Advance time by one frame at 60 FPS.

        # Choose the arrow target offset based on hover state.
        target = 0 if self.hovered else -20

        # Smoothly move the arrow toward the target.
        self.arrow_offset += (target - self.arrow_offset) * 0.20

    def draw(self) -> None:

        # Compute the arrow's x position.
        arrow_x = self.text.x - 30 + self.arrow_offset
        # Add a small vertical wobble.
        arrow_y = self.text.y + 4 + math.sin(self.time * 8) * 2

        arrow = [  # Build the arrow polygon for this frame.
            (arrow_x, arrow_y + 6),  # Set the arrow's top point.
            (arrow_x + 16, arrow_y + 16),  # Set the arrow's tip point.
            (arrow_x, arrow_y + 26),  # Set the arrow's bottom point.
        ]

        if self.hovered:  # Only draw the arrow when the item is hovered.
            arcade.draw_polygon_filled(  # Draw the arrow as a filled triangle.
                arrow,
                # Use white so the arrow matches the menu style.
                arcade.color.WHITE
            )

        self.text.color = (  # Choose the label color based on hover state.
            arcade.color.YELLOW  # Use yellow when hovered.
            if self.hovered  # Check whether the item is hovered.
            else arcade.color.WHITE  # Use white otherwise.
        )

        self.text.draw()  # Draw the label text.

    def contains(self, x: float, y: float) -> bool:

        return (  # Return whether the point lies inside the text bounds.
            # Check the x range.
            self.text.x <= x <= self.text.x + self.text.content_width
            and  # Require both x and y to be in range.
            # Check the y range.
            self.text.y <= y <= self.text.y + self.text.content_height
        )
