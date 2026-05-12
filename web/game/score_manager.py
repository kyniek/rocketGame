from typing import Callable


class ScoreManager:
    """Manages player score with observer pattern support."""

    def __init__(self):
        """Initialize with 0 points."""
        self.score = 0
        self._callbacks: list[Callable[[int], None]] = []

    def add_points(self, amount: int) -> int:
        """Add points to score."""
        self.score += amount
        for callback in self._callbacks:
            callback(self.score)
        return self.score

    def subtract_points(self, amount: int) -> int:
        """Subtract points from score."""
        self.score -= amount
        for callback in self._callbacks:
            callback(self.score)
        return self.score

    def reset(self) -> None:
        """Reset score to 0."""
        self.score = 0

    def on_score_changed(self, callback: Callable[[int], None]) -> None:
        """Subscribe to score change events."""
        self._callbacks.append(callback)
