import pytest
from ..models.rocket import Rocket
from ..game_constants import GameConstants


class TestRocket:
    """Tests for Rocket class."""

    def test_rocket_initial_position(self):
        """Should start at correct position."""
        rocket = Rocket()
        assert rocket.col == 0
        assert rocket.row == 0

    def test_rocket_initial_position_custom(self):
        """Should start at custom position."""
        rocket = Rocket(col=5, row=2)
        assert rocket.col == 5
        assert rocket.row == 2

    def test_rocket_move_up(self):
        """Row should increase, capped at 2."""
        rocket = Rocket(row=1)
        rocket.move_up()
        assert rocket.row == 2
        rocket.move_up()  # Should stay at 2
        assert rocket.row == 2

    def test_rocket_move_down(self):
        """Row should decrease, capped at 0."""
        rocket = Rocket(row=1)
        rocket.move_down()
        assert rocket.row == 0
        rocket.move_down()  # Should stay at 0
        assert rocket.row == 0

    def test_rocket_move_forward_pure(self):
        """Should return col+1 without modifying state."""
        rocket = Rocket(col=5, row=1)
        next_col = rocket.move_forward()
        assert next_col == 6
        assert rocket.col == 5  # Original position unchanged

    def test_rocket_reset(self):
        """Should update position correctly."""
        rocket = Rocket(col=1, row=0)
        rocket.reset(10, 2)
        assert rocket.col == 10
        assert rocket.row == 2

    def test_rocket_reset_clamps_row(self):
        """Reset should clamp row to valid range."""
        rocket = Rocket()
        rocket.reset(0, 5)  # Row > MAX_ROW
        assert rocket.row == 2
        rocket.reset(0, -1)  # Row < MIN_ROW
        assert rocket.row == 0

    def test_rocket_initial_pixel_position(self):
        """Should initialize x, y based on col, row."""
        rocket = Rocket(col=0, row=0)
        cell_size = GameConstants.WINDOW_WIDTH / GameConstants.GRID_COLS
        assert rocket.x == 0.0
        assert rocket.y == 0.0

        rocket = Rocket(col=3, row=2)
        assert rocket.x == 3 * cell_size
        assert rocket.y == 2 * cell_size

    def test_rocket_initial_animation_state(self):
        """Should start with animation disabled."""
        rocket = Rocket()
        assert rocket.is_animating is False
        assert rocket.anim_progress == 0.0

    def test_rocket_start_animation(self):
        """Should set up animation state correctly."""
        rocket = Rocket(col=0, row=0)
        cell_size = GameConstants.WINDOW_WIDTH / GameConstants.GRID_COLS

        rocket.start_animation(3, 2)

        assert rocket.is_animating is True
        assert rocket.anim_start_x == 0.0
        assert rocket.anim_start_y == 0.0
        assert rocket.anim_end_x == 3 * cell_size
        assert rocket.anim_end_y == 2 * cell_size
        assert rocket.anim_progress == 0.0

    def test_rocket_animation_update(self):
        """Should interpolate position during animation."""
        rocket = Rocket(col=0, row=0)
        cell_size = GameConstants.WINDOW_WIDTH / GameConstants.GRID_COLS

        rocket.start_animation(5, 0)
        
        # Simulate time passing (animation duration is 0.2 seconds)
        rocket.update_animation(0.1)  # Half of 0.2s = 50% progress
        
        assert rocket.is_animating is True
        assert rocket.anim_progress > 0.0
        assert rocket.anim_progress < 1.0
        # At 50% progress, x should be halfway between 0 and 5*cell_size
        expected_x = 2.5 * cell_size
        assert abs(rocket.x - expected_x) < 0.1

    def test_rocket_animation_complete(self):
        """Should complete animation and snap to final position."""
        rocket = Rocket(col=0, row=0)
        cell_size = GameConstants.WINDOW_WIDTH / GameConstants.GRID_COLS

        rocket.start_animation(3, 1)
        
        # Simulate full animation duration
        completed = rocket.update_animation(0.2)  # Full 0.2s
        
        assert completed is True
        assert rocket.is_animating is False
        assert rocket.anim_progress == 1.0
        assert rocket.x == 3 * cell_size
        assert rocket.y == 1 * cell_size

    def test_rocket_animation_no_op_when_not_animating(self):
        """update_animation should return True immediately if not animating."""
        rocket = Rocket()
        result = rocket.update_animation(0.1)
        assert result is True
        assert rocket.is_animating is False

    def test_rocket_reset_cancels_animation(self):
        """Reset should cancel any ongoing animation."""
        rocket = Rocket(col=0, row=0)
        
        rocket.start_animation(5, 2)
        assert rocket.is_animating is True
        
        rocket.reset(1, 1)
        
        assert rocket.is_animating is False
        assert rocket.anim_progress == 0.0
        # Position should be set directly without animation
        cell_size = GameConstants.WINDOW_WIDTH / GameConstants.GRID_COLS
        assert rocket.x == 1 * cell_size
        assert rocket.y == 1 * cell_size

    def test_rocket_lerp(self):
        """_lerp should interpolate correctly."""
        rocket = Rocket()
        
        assert rocket._lerp(0.0, 10.0, 0.0) == 0.0
        assert rocket._lerp(0.0, 10.0, 1.0) == 10.0
        assert rocket._lerp(0.0, 10.0, 0.5) == 5.0
        assert rocket._lerp(100.0, 200.0, 0.25) == 125.0
