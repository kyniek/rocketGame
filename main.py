#!/usr/bin/env python3
"""Main entry point for the gameRocket POC."""

import arcade

from views.start_view import StartView
from game_constants import GameConstants


class GameWindow(arcade.Window):
    """Custom window that handles resizing and updates game dimensions."""

    def __init__(self, width: int, height: int, title: str):
        """Initialize the game window.

        Args:
            width: Initial window width.
            height: Initial window height.
            title: Window title.
        """
        super().__init__(width, height, title, resizable=True)

    def on_resize(self, width: int, height: int):
        """Handle window resize event.

        Updates cell size and all derived constants when window is resized.

        Args:
            width: New window width.
            height: New window height.
        """
        # Update window dimensions
        GameConstants.WINDOW_WIDTH = width
        GameConstants.WINDOW_HEIGHT = height

        # Recalculate cell size based on new width
        GameConstants.CELL_SIZE = width / GameConstants.GRID_COLS

        # Recalculate grid dimensions
        GameConstants.GRID_WIDTH = GameConstants.GRID_COLS * GameConstants.CELL_SIZE
        GameConstants.GRID_HEIGHT = (GameConstants.ROCKET_MAX_ROW + 1) * GameConstants.CELL_SIZE


def main():
    """Create and run the game window."""
    # Create window with initial size
    window = GameWindow(GameConstants.WINDOW_WIDTH, GameConstants.WINDOW_HEIGHT, GameConstants.WINDOW_TITLE)

    # Get screen size and maximize window
    screen_width, screen_height = arcade.get_display_size()
    window.set_size(screen_width, screen_height)
    window.center_window()
    window.set_location(0, window.get_location()[1])


    # Show start view
    start_view = StartView()
    window.show_view(start_view)

    # Run the game
    arcade.run()


if __name__ == "__main__":
    main()
