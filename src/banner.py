import arcade  # Import the Arcade library used for drawing shapes.
class Banner:

    def __init__(self, start_x, start_y):

        self.x = start_x# Set the initial horizontal position off-screen.
        self.y = start_y # Set the initial vertical position near the top.

        # self.width = 420  # Keep the old fixed width as a reference.
        self.height = 1000  # Set the banner height.
        self.width = 0   # Start with no visible width.

        self.target_x = start_x  # Store the target horizontal position.
        self.target_y = start_y  # Store the target vertical position.

        self.color = (37, 37, 37)  # Set the banner fill color.

        # self.visible = False  # Keep the old visibility flag as a reference.

    def move_to(self, x, y):
            self.target_x = x  # Update the destination x position.
            self.target_y = y  # Update the destination y position.


    def update(self):
        self.x += (self.target_x - self.x) * 0.5  # Smoothly animate x toward the target.
        self.y += (self.target_y - self.y) * 0.5  # Smoothly animate y toward the target.

    def draw(self):

        points = [  # Build the main banner polygon points.
            (self.x - 200, self.y),  # Define the top-left corner.
            (self.x + 3000, self.y),  # Define the top-right corner.
            (self.x + 3000 , self.y + self.height),  # Define the bottom-right slanted corner.
            (self.x + 150, self.y + self.height),  # Define the bottom-left slanted corner.
        ]

        arcade.draw_polygon_filled(points, self.color)  # Fill the banner shape with its main color.

