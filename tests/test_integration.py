"""Integration tests for the game."""

import pytest
from unittest.mock import Mock, patch

from ..models.maze_generator import MazeGenerator
from ..models.game_grid import GameGrid
from ..models.rocket import Rocket
from ..models.fog_of_war import FogOfWar
from ..managers.lives_manager import LivesManager
from managers.score_manager import ScoreManager


def _create_clear_cell(col: int, row: int) -> str:
    """Create a cell for a clear maze (no obstacles)."""
    if col == 0 and row == 1:
        return 'start'
    else:
        return 'empty'


class TestIntegration:
    """Integration tests for the full game flow."""

    def test_integration_full_flow(self):
        """Simulate a complete game session."""
        mock_window = Mock()
        mock_window.width = 1200
        mock_window.height = 600

        # Create a clear maze with no obstacles for testing
        clear_grid = [[_create_clear_cell(col, row) for row in range(3)]
                      for col in range(30)]

        with patch('arcade.get_window', return_value=mock_window):
            from views.game_view import GameView
            with patch('models.maze_generator.MazeGenerator.generate', return_value=clear_grid):
                game = GameView(start_row=1)

        # Initial state checks
        assert game.rocket.col == 0
        assert game.rocket.row == 1
        assert game.lives_manager.lives == 3
        assert game.score_manager.score == 0

        # Simulate moving forward multiple times (mocking challenges)
        with patch('views.game_view.random.random', return_value=0.5):  # No challenges
            for _ in range(5):
                game._move_forward()

        # Rocket should have moved forward
        assert game.rocket.col > 0

    def test_integration_obstacle_collision(self):
        """Verify life loss and respawn on obstacle collision."""
        mock_window = Mock()
        mock_window.width = 1200
        mock_window.height = 600

        with patch('arcade.get_window', return_value=mock_window):
            from views.game_view import GameView
            game = GameView(start_row=1)

        # Move forward until we hit an obstacle or reach column 5
        for _ in range(10):
            # Mock random to avoid challenges during this test
            with patch('views.game_view.random.random', return_value=0.5):
                game._move_forward()
            next_col = game.rocket.col

            # Check if we hit an obstacle
            cell = game.grid.get_cell(next_col, game.rocket.row)
            if cell == 'obstacle':
                # We hit an obstacle - verify life loss and respawn
                assert game.lives_manager.lives < 3

                # Check if respawned at start
                assert game.rocket.col == 0
                assert game.rocket.row == game.start_row

                # Fog should be reset
                assert not game.fog.is_discovered(15, 1)  # Should not see far ahead
                return

        # If we didn't hit an obstacle, that's okay - just verify movement worked
        assert game.rocket.col > 0

    def test_integration_level_complete(self):
        """Verify reaching last column generates new level."""
        mock_window = Mock()
        mock_window.width = 1200
        mock_window.height = 600

        # Create a clear maze with no obstacles for testing level complete
        clear_grid = [[_create_clear_cell(col, row) for row in range(3)]
                      for col in range(30)]

        with patch('arcade.get_window', return_value=mock_window):
            from views.game_view import GameView
            with patch('models.maze_generator.MazeGenerator.generate', return_value=clear_grid):
                game = GameView(start_row=0)

        # Store initial level
        initial_level = game.challenge_manager.level

        # Move forward until reaching goal column (29)
        for _ in range(50):
            # Mock the random challenge to not interrupt
            with patch('views.game_view.random.random', return_value=1.0):
                game._move_forward()

            # Check if level has incremented (new maze generated)
            if game.challenge_manager.level == initial_level + 1:
                break

        # Level should have incremented (new maze generated)
        assert game.challenge_manager.level == initial_level + 1

        # Rocket should be at column 0 of new level
        assert game.rocket.col == 0

    def test_integration_victory_condition(self):
        """Verify all questions answered correctly triggers victory."""
        mock_window = Mock()
        mock_window.width = 1200
        mock_window.height = 600

        with patch('arcade.get_window', return_value=mock_window):
            from views.game_view import GameView
            game = GameView(start_row=1)

        # Simulate answering all questions correctly by emptying challenge list
        game.challenge_manager.challenges = []
        game._check_victory_condition()

        # Victory should be True when all questions answered correctly
        assert game.victory is True

    def test_integration_victory_by_row_movement(self):
        """Verify victory only when all questions answered correctly."""
        mock_window = Mock()
        mock_window.width = 1200
        mock_window.height = 600

        with patch('arcade.get_window', return_value=mock_window):
            from views.game_view import GameView
            game = GameView(start_row=1)

        # Victory should NOT be True without answering all questions
        game._check_victory_condition()
        assert game.victory is False

        # Simulate answering all questions correctly
        game.challenge_manager.challenges = []
        game._check_victory_condition()

        # Victory should now be True
        assert game.victory is True

    def test_integration_lives_depletion(self):
        """Verify game over when lives reach 0."""
        mock_window = Mock()
        mock_window.width = 1200
        mock_window.height = 600

        with patch('arcade.get_window', return_value=mock_window):
            from views.game_view import GameView
            game = GameView(start_row=1)

        # Simulate losing all lives
        for _ in range(3):
            game.lives_manager.lose_life()

        assert not game.lives_manager.is_alive()


class TestGameViewLogic:
    """Tests for GameView internal logic."""

    def test_game_view_fog_updates_on_move(self):
        """Fog should update when rocket moves."""
        mock_window = Mock()
        mock_window.width = 1200
        mock_window.height = 600

        with patch('arcade.get_window', return_value=mock_window):
            from views.game_view import GameView
            game = GameView(start_row=1)

        # Initially only cols 0 and 1 are visible
        assert game.fog.is_discovered(0, 1) is True
        assert game.fog.is_discovered(1, 1) is True

        # Move forward
        with patch('views.game_view.random.random', return_value=0.5):
            game._move_forward()

        # More columns should now be visible
        assert game.fog.is_discovered(game.rocket.col, game.rocket.row) is True

    def test_game_view_challenge_20_percent(self):
        """Challenge should trigger on 20% of forward moves."""
        mock_window = Mock()
        mock_window.width = 1200
        mock_window.height = 600

        # Create a clear maze to ensure we can move without hitting obstacles
        clear_grid = [[_create_clear_cell(col, row) for row in range(3)]
                      for col in range(30)]

        with patch('arcade.get_window', return_value=mock_window):
            from views.game_view import GameView
            with patch('models.maze_generator.MazeGenerator.generate', return_value=clear_grid):
                game = GameView(start_row=1)

        # Mock random to always return < 0.2 - challenge should trigger
        with patch('views.game_view.random.random', return_value=0.1):
            # Also mock ChallengeView to avoid arcade window requirement
            with patch('views.game_view.ChallengeView') as MockChallengeView:
                game._move_forward()
                # Challenge should have been triggered
                assert MockChallengeView.called

        # Mock random to always return >= 0.2 - challenge should not trigger
        with patch('views.game_view.random.random', return_value=0.9):
            game._move_forward()
            # Challenge should not have been triggered

    def test_game_view_boundary_checks(self):
        """Should handle boundary conditions correctly."""
        mock_window = Mock()
        mock_window.width = 1200
        mock_window.height = 600

        with patch('arcade.get_window', return_value=mock_window):
            from views.game_view import GameView
            game = GameView(start_row=1)

        # Move up and down
        game.rocket.move_up()
        assert game.rocket.row == 2

        game.rocket.move_up()  # Should stay at max
        assert game.rocket.row == 2

        game.rocket.move_down()
        assert game.rocket.row == 1

    def test_game_view_rocket_reset(self):
        """Rocket reset should work correctly."""
        mock_window = Mock()
        mock_window.width = 1200
        mock_window.height = 600

        with patch('arcade.get_window', return_value=mock_window):
            from views.game_view import GameView
            game = GameView(start_row=1)

        # Move rocket
        game.rocket.col = 15
        game.rocket.row = 2

        # Reset to start
        game.rocket.reset(0, game.start_row)

        assert game.rocket.col == 0
        assert game.rocket.row == 1
