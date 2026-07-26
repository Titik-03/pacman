import arcade  # Import Arcade for text and shape drawing.
import math  # Import math for the sine-based hover animation.


class MenuItem:

    def __init__(self, label: str, x: float, y: float):

        self.base_x = x  # Store the original x position.
        self.base_y = y  # Store the original y position.

        self.offset = 0  # Keep a generic offset value for layout or animation.

        self.font_size = 32  # Set the menu text size.

        self.arrow_offset = -20  # Start the arrow slightly left of the text.
        self.time = 0  # Track elapsed time for animation.

        self.text = arcade.Text(  # Create the text object for the menu item.
            label,  # Use the provided label string.
            x,  # Use the provided x coordinate.
            y,  # Use the provided y coordinate.
            arcade.color.WHITE,  # Start with white text.
            32,  # Use a 32-point font size.
            bold=True,  # Draw the label in bold.
        )

        self.hovered = False  # Track whether the mouse is over the item.

        self.arrow = [  # Build the initial arrow polygon points.
            (self.text.x + self.arrow_offset, self.text.y + 8),  # Set the top point.
            (self.text.x + self.arrow_offset + 18, self.text.y + 18),  # Set the tip point.
            (self.text.x + self.arrow_offset, self.text.y + 28),  # Set the bottom point.
        ]

    def update(self):

        self.time += 1 / 60  # Advance time by one frame at 60 FPS.

        target = 0 if self.hovered else -20  # Choose the arrow target offset based on hover state.

        self.arrow_offset += (target - self.arrow_offset) * 0.20  # Smoothly move the arrow toward the target.

    def draw(self):

        arrow_x = self.text.x - 20 + self.arrow_offset  # Compute the arrow's x position.
        arrow_y = self.text.y + math.sin(self.time * 8) * 2  # Add a small vertical wobble.

        arrow = [  # Build the arrow polygon for this frame.
            (arrow_x, arrow_y + 8),  # Set the arrow's top point.
            (arrow_x + 18, arrow_y + 18),  # Set the arrow's tip point.
            (arrow_x, arrow_y + 28),  # Set the arrow's bottom point.
        ]

        if self.hovered:  # Only draw the arrow when the item is hovered.
            arcade.draw_polygon_filled(  # Draw the arrow as a filled triangle.
                arrow,
                arcade.color.WHITE  # Use white so the arrow matches the menu style.
            )

        self.text.color = (  # Choose the label color based on hover state.
            arcade.color.YELLOW  # Use yellow when hovered.
            if self.hovered  # Check whether the item is hovered.
            else arcade.color.WHITE  # Use white otherwise.
        )

        self.text.draw()  # Draw the label text.

    def contains(self, x, y):

        return (  # Return whether the point lies inside the text bounds.
            self.text.x <= x <= self.text.x + self.text.content_width  # Check the x range.
            and  # Require both x and y to be in range.
            self.text.y <= y <= self.text.y + self.text.content_height  # Check the y range.
        )


