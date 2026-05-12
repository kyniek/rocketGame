from typing import Callable

from .constants import GameConstants


class LivesManager:
    """Manages player lives with observer pattern support."""

    def __init__(self):
        """Initialize with 3 lives."""
        self.lives = GameConstants.STARTING_LIVES
        self._callbacks: list[Callable[[int], None]] = []

    def lose_life(self) -> int:
        """Decrement lives by 1."""
        if self.lives > 0:
            self.lives -= 1
            for callback in self._callbacks:
                callback(self.lives)
        return self.lives

    def reset(self) -> None:
        """Reset lives to starting value."""
        self.lives = GameConstants.STARTING_LIVES

    def is_alive(self) -> bool:
        """Check if player has any lives remaining."""
        return self.lives > 0

    def on_life_lost(self, callback: Callable[[int], None]) -> None:
        """Subscribe to life lost events."""
        self._callbacks.append(callback)
