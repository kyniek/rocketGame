import pytest
from unittest.mock import Mock
from ..managers.score_manager import ScoreManager


class TestScoreManager:
    """Tests for ScoreManager class."""

    def test_score_manager_initial(self):
        """Should start with 0 points."""
        manager = ScoreManager()
        assert manager.score == 0

    def test_score_manager_add_points(self):
        """Should add points correctly."""
        manager = ScoreManager()
        result = manager.add_points(10)
        assert result == 10
        assert manager.score == 10

        result = manager.add_points(5)
        assert result == 15
        assert manager.score == 15

    def test_score_manager_reset(self):
        """Should reset to 0."""
        manager = ScoreManager()
        manager.add_points(100)
        manager.reset()
        assert manager.score == 0

    def test_score_manager_callback(self):
        """Should call callback with new score."""
        manager = ScoreManager()
        callback = Mock()
        manager.on_score_changed(callback)

        manager.add_points(10)
        callback.assert_called_once_with(10)

        manager.add_points(5)
        assert callback.call_count == 2
