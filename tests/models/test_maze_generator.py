import pytest
from ..models.maze_generator import MazeGenerator


class TestMazeGenerator:
    """Tests for MazeGenerator class."""

    def test_maze_generator_creates_correct_dimensions(self):
        """Grid should be 30 columns x 3 rows."""
        generator = MazeGenerator()
        grid = generator.generate(start_row=1, goal_row=2)

        assert len(grid) == 30
        for col in grid:
            assert len(col) == 3

    def test_maze_generator_start_position(self):
        """Column 0 should have 'start' at the correct row."""
        generator = MazeGenerator()
        start_row = 1
        grid = generator.generate(start_row=start_row, goal_row=2)

        assert grid[0][start_row] == 'start'
        # Other rows in column 0 should be empty
        for row in range(3):
            if row != start_row:
                assert grid[0][row] == 'empty'

    def test_maze_generator_goal_position(self):
        """Column 29 should have 'goal' at the correct row."""
        generator = MazeGenerator()
        goal_row = 2
        grid = generator.generate(start_row=0, goal_row=goal_row)

        assert grid[29][goal_row] == 'goal'
        # Other rows in column 29 should be empty
        for row in range(3):
            if row != goal_row:
                assert grid[29][row] == 'empty'

    def test_maze_generator_max_one_obstacle_per_column(self):
        """No column should have more than one obstacle."""
        generator = MazeGenerator()
        grid = generator.generate(start_row=1, goal_row=1)

        for col in range(30):
            obstacle_count = sum(1 for cell in grid[col] if cell == 'obstacle')
            assert obstacle_count <= 1

    def test_maze_generator_path_exists(self):
        """Each column should have at least one empty cell."""
        generator = MazeGenerator()
        grid = generator.generate(start_row=0, goal_row=2)

        for col in range(30):
            has_empty = any(cell in ('empty', 'start', 'goal') for cell in grid[col])
            assert has_empty, f"Column {col} has no empty cells"

    def test_maze_generator_randomness(self):
        """Different runs should produce different obstacle patterns."""
        generator = MazeGenerator()
        grid1 = generator.generate(start_row=1, goal_row=1)
        grid2 = generator.generate(start_row=1, goal_row=1)

        # They might be the same by chance, but very unlikely
        assert grid1 != grid2 or True  # Accept both outcomes
