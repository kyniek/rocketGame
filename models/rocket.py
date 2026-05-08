from game_constants import GameConstants


class Rocket:
    """Represents the rocket with position and movement logic."""

    def __init__(self, col: int = 0, row: int = 0):
        """Initialize rocket at given position.

        Args:
            col: Initial column (default 0).
            row: Initial row (0-2, default 0).
        """
        self.col = col
        self.row = row
        # Continuous pixel position for smooth animation
        cell_size = GameConstants.WINDOW_WIDTH / GameConstants.GRID_COLS
        self.x = col * cell_size
        self.y = row * cell_size

        # Animation state
        self.is_animating = False
        self.anim_start_x = 0.0
        self.anim_start_y = 0.0
        self.anim_end_x = 0.0
        self.anim_end_y = 0.0
        self.anim_progress = 0.0

    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation between a and b.

        Args:
            a: Start value.
            b: End value.
            t: Interpolation factor (0.0 to 1.0).

        Returns:
            Interpolated value.
        """
        return a + (b - a) * t

    def start_animation(self, target_col: int, target_row: int):
        """Start smooth animation to a new grid position.

        Args:
            target_col: Target column.
            target_row: Target row.
        """
        cell_size = GameConstants.WINDOW_WIDTH / GameConstants.GRID_COLS

        # Save current position as start
        self.anim_start_x = self.x
        self.anim_start_y = self.y

        # Calculate target pixel position
        self.anim_end_x = target_col * cell_size
        self.anim_end_y = target_row * cell_size

        # Reset progress and mark as animating
        self.anim_progress = 0.0
        self.is_animating = True

    def update_animation(self, dt: float) -> bool:
        """Update animation progress.

        Args:
            dt: Delta time in seconds since last frame.

        Returns:
            True when animation is complete.
        """
        if not self.is_animating:
            return True

        # Update progress based on animation duration
        self.anim_progress += dt / GameConstants.ROCKET_ANIMATION_DURATION

        if self.anim_progress >= 1.0:
            # Animation complete - snap to final position
            self.x = self.anim_end_x
            self.y = self.anim_end_y
            self.is_animating = False
            self.anim_progress = 1.0
            return True

        # Interpolate position
        self.x = self._lerp(self.anim_start_x, self.anim_end_x, self.anim_progress)
        self.y = self._lerp(self.anim_start_y, self.anim_end_y, self.anim_progress)

        return False

    def move_up(self) -> None:
        """Increase row by 1, capped at MAX_ROW."""
        if self.row < GameConstants.MAX_ROW:
            self.row += 1

    def move_down(self) -> None:
        """Decrease row by 1, capped at MIN_ROW."""
        if self.row > GameConstants.MIN_ROW:
            self.row -= 1

    def move_forward(self) -> int:
        """Return the next column without modifying state.

        Returns:
            col + 1
        """
        return self.col + 1

    def reset(self, col: int, row: int) -> None:
        """Reset rocket to a new position.

        Args:
            col: New column.
            row: New row (0-2).
        """
        self.col = col
        self.row = max(GameConstants.MIN_ROW, min(row, GameConstants.MAX_ROW))

        # Set pixel position directly (no animation for reset)
        cell_size = GameConstants.WINDOW_WIDTH / GameConstants.GRID_COLS
        self.x = col * cell_size
        self.y = self.row * cell_size

        # Cancel any ongoing animation
        self.is_animating = False
        self.anim_progress = 0.0
