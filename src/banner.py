import arcade  # Import the Arcade library used for drawing shapes.


class Banner:
    """Animated decorative background banner for menus."""

    def __init__(self, start_x: float, start_y: float) -> None:
        """Initialize banner position, dimensions, and color."""
        self.x: float = float(start_x)
        self.y: float = float(start_y)
        self.height: float = 1000.0
        self.target_height: float = 1000.0
        self.width: float = 0.0
        self.target_x: float = float(start_x)
        self.target_y: float = float(start_y)
        self.color = (203, 166, 247)  # Set the banner fill color.

    def move_to(self, x: float, y: float) -> None:
        """Set the target position for animation."""
        self.target_x = x  # Update the destination x position.
        self.target_y = y  # Update the destination y position.

    def update(self) -> None:
        """Smoothly interpolate position and height toward target values."""
        # Smoothly animate position and height
        # (changed to 0.15 for smoother transitions)
        self.x += (self.target_x - self.x) * 0.15
        self.y += (self.target_y - self.y) * 0.15
        self.height += (self.target_height - self.height) * 0.15

    def draw(self) -> None:
        """Render the banner polygon on the screen."""
        points = [  # Build the main banner polygon points.
            (self.x - 200, self.y),  # Define the top-left corner.
            # Extended from 3000 to 4000 to guarantee screen coverage
            (self.x + 4000, self.y),
            (self.x + 4000, self.y + self.height),
            # Define the bottom-left slanted corner.
            (self.x + 150, self.y + self.height),
        ]
        # Fill the banner shape with its main color.
        arcade.draw_polygon_filled(points, self.color)
