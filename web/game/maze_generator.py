import random

from .constants import GameConstants


class MazeGenerator:
    """Generates a 30x5 maze grid with obstacles and start position."""

    def generate(self, start_row: int) -> list[list[str]]:
        """Generate a maze grid.

        Args:
            start_row: Row index (0-4) for the start position in column 0.

        Returns:
            A 30x5 grid represented as list[list[str]] with values:
            'empty', 'obstacle', or 'start'.
        """
        grid = [['' for _ in range(GameConstants.ROWS)] for _ in range(GameConstants.COLS)]

        grid[0][start_row] = 'start'

        current_row = start_row
        for col in range(1, GameConstants.COLS):
            direction = random.choice([-1, 0, 1])

            new_row = current_row + direction
            if new_row < 0:
                new_row = 0
            elif new_row > GameConstants.ROWS - 1:
                new_row = GameConstants.ROWS - 1

            grid[col][new_row] = 'empty'
            if current_row != new_row:
                grid[col][current_row] = 'empty'
            if col == GameConstants.COLS - 1:
                for row in range(0, GameConstants.ROWS):
                    grid[col][row] = 'empty'

            current_row = new_row

        for col in range(GameConstants.COLS):
            for row in range(GameConstants.ROWS):
                if grid[col][row] not in ('empty', 'start'):
                    grid[col][row] = 'obstacle'

        return grid

    def _create_empty_cell(self, col: int, row: int) -> str:
        """Create an empty cell value."""
        return 'empty'
