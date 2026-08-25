import sys
import os
import arcade
from src.main_menu import MainMenu

def main():

    window = arcade.Window(1920, 1080, "Pac-man", fullscreen=False)
    main_menu = MainMenu(window)
    window.show_view(main_menu)
    arcade.run()


if __name__ == "__main__":
    main()

