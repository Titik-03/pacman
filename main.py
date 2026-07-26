import sys
import os

# Add src directory to python module search path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import arcade
from main_menu import MainMenu


def main():
    window = arcade.Window(1920, 1080, "Pac-man", resizable=True, fullscreen=True)
    main_menu = MainMenu(window)
    window.show_view(main_menu)
    arcade.run()


if __name__ == "__main__":
    main()

