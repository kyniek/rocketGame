from typing import Callable

from game_constants import GameConstants


class LivesManager:
    """Manages player lives with observer pattern support."""

    def __init__(self):
        """Initialize with 3 lives."""
        self.lives = GameConstants.STARTING_LIVES
        self._callbacks: list[Callable[[int], None]] = []

    def lose_life(self) -> int:
        """Decrement lives by 1.

        Returns:
            Remaining lives (never below 0).
        """
        if self.lives > 0:
            self.lives -= 1
            for callback in self._callbacks:
                callback(self.lives)
        return self.lives

    def reset(self) -> None:
        """Reset lives to starting value."""
        self.lives = GameConstants.STARTING_LIVES

    def is_alive(self) -> bool:
        """Check if player has any lives remaining.

        Returns:
            True if lives > 0, False otherwise.
        """
        return self.lives > 0

    def on_life_lost(self, callback: Callable[[int], None]) -> None:
        """Subscribe to life lost events.

        Args:
            callback: Function called with remaining lives when a life is lost.
        """
        self._callbacks.append(callback)
