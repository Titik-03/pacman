import arcade  # Import the Arcade library used for drawing shapes.


class Banner:

    def __init__(self):

        self.x = -450  # Set the initial horizontal position off-screen.
        self.y = 650  # Set the initial vertical position near the top.

        # self.width = 420  # Keep the old fixed width as a reference.
        self.height = 55  # Set the banner height.
        self.width = 0  # Start with no visible width.
        self.target_width = 0  # Store the width the banner should animate toward.

        self.target_x = -500  # Store the target horizontal position.
        self.target_y = 0  # Store the target vertical position.

        self.color = (240, 40, 40)  # Set the banner fill color.

        # self.visible = False  # Keep the old visibility flag as a reference.

    def move_to(self, x, y, width):
            self.target_x = x  # Update the destination x position.
            self.target_y = y  # Update the destination y position.
            self.target_width = width  # Update the destination width.

    def update(self):

        self.width += (self.target_width - self.width) * 0.5  # Smoothly animate width toward the target.
        self.x += (self.target_x - self.x) * 0.5  # Smoothly animate x toward the target.
        self.y += (self.target_y - self.y) * 0.5  # Smoothly animate y toward the target.

    def draw(self):

        shadow = [  # Build the shadow polygon points.
            (self.x + 8, self.y - 8),  # Offset the top-left shadow corner.
            (self.x + self.width + 8, self.y - 8),  # Offset the top-right shadow corner.
            (self.x + self.width - 40 + 8, self.y + self.height - 8),  # Offset the bottom-right shadow corner.
            (self.x - 40 + 8, self.y + self.height - 8),  # Offset the bottom-left shadow corner.
        ]

        arcade.draw_polygon_filled(  # Draw the shadow behind the banner.
            shadow,
            (0, 0, 0, 120)  # Use a semi-transparent black shadow color.
        )

        points = [  # Build the main banner polygon points.
            (self.x, self.y),  # Define the top-left corner.
            (self.x + self.width, self.y),  # Define the top-right corner.
            (self.x + self.width - 40, self.y + self.height),  # Define the bottom-right slanted corner.
            (self.x - 40, self.y + self.height),  # Define the bottom-left slanted corner.
        ]

        arcade.draw_polygon_filled(points, self.color)  # Fill the banner shape with its main color.

        arcade.draw_polygon_outline(  # Draw a border around the banner.
            points,
            arcade.color.WHITE,  # Use white for the outline color.
            line_width=2  # Make the border clearly visible.
        )

        accent = [  # Build the decorative accent polygon points.
            (self.x + 20, self.y + self.height - 12),  # Set the accent's upper-left point.
            (self.x + 120, self.y + self.height - 12),  # Set the accent's upper-right point.
            (self.x + 100, self.y + self.height - 4),  # Set the accent's lower-right point.
            (self.x, self.y + self.height - 4),  # Set the accent's lower-left point.
        ]

        arcade.draw_polygon_filled(  # Draw the white accent shape on top of the banner.
            accent,
            arcade.color.WHITE  # Use white so the accent stands out.
        )
