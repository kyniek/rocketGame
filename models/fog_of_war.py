from game_constants import GameConstants


class FogOfWar:
    """Tracks which cells are visible to the player."""

    def __init__(self):
        """Initialize fog of war with initial state (cols 0 and 1 visible)."""
        self._discovered = [[False for _ in range(GameConstants.ROWS)]
                           for _ in range(GameConstants.COLS)]
        # Set initial state: columns 0 and 1 are visible
        for col in range(2):
            for row in range(GameConstants.ROWS):
                self._discovered[col][row] = True

    def update(self, current_col: int, current_row: int) -> None:
        """Mark cells as discovered based on current position.

        Args:
            current_col: Current column of the rocket.
            current_row: Current row of the rocket.
        """
        # Mark all cells with col <= current_col as discovered
        for col in range(current_col + 1):
            for row in range(GameConstants.ROWS):
                self._discovered[col][row] = True

        # Mark column current_col + 1 as discovered (one step ahead)
        next_col = current_col + 1
        if next_col < GameConstants.COLS:
            for row in range(GameConstants.ROWS):
                self._discovered[next_col][row] = True

    def reset(self) -> None:
        """Reset to initial state - only columns 0 and 1 visible."""
        for col in range(GameConstants.COLS):
            for row in range(GameConstants.ROWS):
                self._discovered[col][row] = False

        # Only columns 0 and 1 are visible initially
        for col in range(2):
            for row in range(GameConstants.ROWS):
                self._discovered[col][row] = True

    def is_discovered(self, col: int, row: int) -> bool:
        """Check if a cell is discovered.

        Args:
            col: Column index.
            row: Row index.

        Returns:
            True if the cell is discovered, False otherwise.
        """
        if not (0 <= col < GameConstants.COLS and 0 <= row < GameConstants.ROWS):
            return False
        return self._discovered[col][row]
