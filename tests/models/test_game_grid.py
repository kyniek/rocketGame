import pytest
from ..models.game_grid import GameGrid


class TestGameGrid:
    """Tests for GameGrid class."""

    @pytest.fixture
    def grid(self):
        """Create a simple test grid (30 columns x 3 rows)."""
        # Create a minimal valid grid for testing
        grid_data = []
        for col in range(30):
            row_data = ['empty', 'empty', 'empty']
            if col == 0:
                row_data[0] = 'start'
            elif col == 29:
                row_data[1] = 'goal'
            grid_data.append(row_data)
        return GameGrid(grid_data)

    def test_game_grid_get_cell(self, grid):
        """Should return correct cell value."""
        assert grid.get_cell(0, 0) == 'start'
        assert grid.get_cell(15, 1) == 'empty'
        assert grid.get_cell(29, 1) == 'goal'

    def test_game_grid_set_cell(self, grid):
        """Should update cell value correctly."""
        assert grid.set_cell(0, 1, 'obstacle') is True
        assert grid.get_cell(0, 1) == 'obstacle'

    def test_game_grid_is_walkable_empty(self, grid):
        """'empty' should return True."""
        assert grid.is_walkable(0, 1) is True

    def test_game_grid_is_walkable_obstacle(self, grid):
        """'obstacle' should return False."""
        # Set an obstacle
        grid.set_cell(5, 0, 'obstacle')
        assert grid.is_walkable(5, 0) is False

    def test_game_grid_is_walkable_start_goal(self, grid):
        """'start' and 'goal' should return True."""
        assert grid.is_walkable(0, 0) is True
        assert grid.is_walkable(29, 1) is True

    def test_game_grid_boundary_checks(self, grid):
        """Should handle out-of-bounds gracefully."""
        assert grid.get_cell(-1, 0) is None
        assert grid.get_cell(30, 0) is None  # Out of bounds (max valid is 29)
        assert grid.get_cell(0, -1) is None
        assert grid.get_cell(0, 3) is None

        assert grid.is_walkable(-1, 0) is False
        assert grid.is_walkable(30, 0) is False

    def test_game_grid_set_cell_out_of_bounds(self, grid):
        """set_cell should return False for out-of-bounds."""
        assert grid.set_cell(-1, 0, 'test') is False
        assert grid.set_cell(30, 0, 'test') is False
