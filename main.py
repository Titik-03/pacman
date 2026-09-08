import sys
from pathlib import Path
import arcade
from src.main_menu import MainMenu
from src.levels import ConfigError, ConfigParser


def main() -> None:
    """Main entry point for the Pac-man application."""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config.json>", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    if not Path(config_path).is_file():
        print(
            f"Error: Configuration file '{config_path}' not found.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        config_parser = ConfigParser(config_path)
    except ConfigError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    window = arcade.Window(1920, 1080, "Pac-man", fullscreen=True)
    main_menu = MainMenu(window, config_parser=config_parser)
    window.show_view(main_menu)
    arcade.run()


if __name__ == "__main__":
    main()
