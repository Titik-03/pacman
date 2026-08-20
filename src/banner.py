import arcade  # Import the Arcade library used for drawing shapes.

class Banner:
    def __init__(self, start_x, start_y):
        self.x = start_x# Set the initial horizontal position off-screen.
        self.y = start_y # Set the initial vertical position near the top.
        self.height = 1000  # Set the banner height.
        self.target_height = 1000 # ADDED: Target height for dynamic expansion
        self.width = 0   # Start with no visible width.
        self.target_x = start_x  # Store the target horizontal position.
        self.target_y = start_y  # Store the target vertical position.
        self.color = (203, 166, 247) # Set the banner fill color.

    def move_to(self, x, y):
        self.target_x = x  # Update the destination x position.
        self.target_y = y  # Update the destination y position.

    def update(self):
        # Smoothly animate position and height (changed to 0.15 for smoother transitions)
        self.x += (self.target_x - self.x) * 0.15 
        self.y += (self.target_y - self.y) * 0.15 
        self.height += (self.target_height - self.height) * 0.15

    def draw(self):
        points = [  # Build the main banner polygon points.
            (self.x - 200, self.y),  # Define the top-left corner.
            (self.x + 4000, self.y),  # Extended from 3000 to 4000 to guarantee screen coverage
            (self.x + 4000 , self.y + self.height),  
            (self.x + 150, self.y + self.height),  # Define the bottom-left slanted corner.
        ]
        arcade.draw_polygon_filled(points, self.color)  # Fill the banner shape with its main color.


