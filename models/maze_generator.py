import random

from game_constants import GameConstants


class MazeGenerator:
    """Generates a 30x3 maze grid with obstacles and start position."""

    def generate(self, start_row: int) -> list[list[str]]:
        """Generate a maze grid.

        Args:
            start_row: Row index (0-2) for the start position in column 0.

        Returns:
            A 30x3 grid represented as list[list[str]] with values:
            'empty', 'obstacle', or 'start'.
        """
        # Initialize 30x3 grid with all cells as 'obstacle'
        grid = [['' for _ in range(GameConstants.ROWS)] for _ in range(GameConstants.COLS)]

        # Set start position (column 0)
        grid[0][start_row] = 'start'

        # Create path from start to goal by iterating through columns
        # At each step, randomly move up, down, or stay in the same row
        current_row = start_row
        for col in range(1, GameConstants.COLS):
            # Randomly choose to move up (-1), down (+1), or stay (0)
            direction = random.choice([-1, 0, 1])
            
            # Calculate new row, ensuring it stays within bounds [0, 2]
            new_row = current_row + direction
            if new_row < 0:
                new_row = 0
            elif new_row > GameConstants.ROWS - 1:
                new_row = GameConstants.ROWS - 1
            
            # Mark the cell as empty (part of the path)
            grid[col][new_row] = 'empty'
            if current_row != new_row:
                grid[col][current_row] = 'empty'
            if col == GameConstants.COLS - 1 :
                for row in range(0, GameConstants.ROWS ):
                    grid[col][row] = 'empty'
            
            # Update current row for next iteration
            current_row = new_row

        # Change all cells that are not 'empty' or 'start' to 'obstacle'
        for col in range(GameConstants.COLS):
            for row in range(GameConstants.ROWS):
                if grid[col][row] not in ('empty', 'start'):
                    grid[col][row] = 'obstacle'

        return grid

    def _create_empty_cell(self, col: int, row: int) -> str:
        """Create an empty cell value."""
        return 'empty'
