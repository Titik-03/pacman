import arcade

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Pac-man: View Switching Example"

# ==========================================
# SCREEN 1: THE START MENU VIEW
# ==========================================
class MenuView(arcade.View):
    def on_show_view(self):
        """Runs once immediately when we switch to this view."""
        # Set background to a deep red/maroon
        arcade.set_background_color(arcade.color.DARK_RED)

    def on_draw(self):
        self.clear()
        
        # Display instructions using self.window dimensions
        arcade.draw_text(
            "PAC-MAN START SCREEN", 
            self.window.width / 2, 
            self.window.height / 2 + 50, 
            arcade.color.YELLOW, 
            font_size=32, 
            anchor_x="center"
        )
        
        arcade.draw_text(
            "Press [ENTER] or Click to Start", 
            self.window.width / 2, 
            self.window.height / 2 - 20, 
            arcade.color.WHITE, 
            font_size=18, 
            anchor_x="center"
        )

    # Trigger switch via Mouse Click
    def on_mouse_press(self, x, y, button, modifiers):
        self.start_game()

    # Trigger switch via Keyboard [ENTER]
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            self.start_game()

    def start_game(self):
        # Create the Game Screen instance
        game_screen = GamePlayView()
        
        # Tell our window to transition to this new view!
        self.window.show_view(game_screen)


# ==========================================
# SCREEN 2: THE ACTIVE GAME SCREEN VIEW
# ==========================================
class GamePlayView(arcade.View):
    def on_show_view(self):
        # Set classic Pac-man black background
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        
        # Draw game visual indicators
        arcade.draw_text(
            "Game Is Running...", 
            self.window.width / 2, 
            self.window.height / 2, 
            arcade.color.BLUE, 
            font_size=24, 
            anchor_x="center"
        )
        
        # Draw our temporary player representation (yellow circle)
        arcade.draw_circle_filled(
            self.window.width / 2, 
            self.window.height / 2 - 80, 
            30, 
            arcade.color.YELLOW
        )


# ==========================================
# MAIN DRIVER
# ==========================================
def main():
    # 1. Create a single window object
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    
    # 2. Instantiate our initial view
    menu_screen = MenuView()
    
    # 3. Show our starting view
    window.show_view(menu_screen)
    
    # 4. Start the engine loop
    arcade.run()

if __name__ == "__main__":
    main()