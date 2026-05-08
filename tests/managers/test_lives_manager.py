import pytest
from unittest.mock import Mock
from ..managers.lives_manager import LivesManager


class TestLivesManager:
    """Tests for LivesManager class."""

    def test_lives_manager_initial(self):
        """Should start with 3 lives."""
        manager = LivesManager()
        assert manager.lives == 3

    def test_lives_manager_lose_life(self):
        """Should decrement lives correctly."""
        manager = LivesManager()
        manager.lose_life()
        assert manager.lives == 2
        manager.lose_life()
        assert manager.lives == 1

    def test_lives_manager_no_negative(self):
        """Lives should not go below 0."""
        manager = LivesManager()
        for _ in range(5):  # Try to lose more than available
            manager.lose_life()
        assert manager.lives == 0

    def test_lives_manager_reset(self):
        """Should reset to 3 lives."""
        manager = LivesManager()
        manager.lose_life()
        manager.reset()
        assert manager.lives == 3

    def test_lives_manager_callback(self):
        """Should call callback with remaining lives."""
        manager = LivesManager()
        callback = Mock()
        manager.on_life_lost(callback)

        manager.lose_life()
        callback.assert_called_once_with(2)

        manager.lose_life()
        assert callback.call_count == 2

    def test_lives_manager_is_alive(self):
        """Should return True when lives > 0."""
        manager = LivesManager()
        assert manager.is_alive() is True
        manager.lose_life()
        assert manager.is_alive() is True
        manager.lose_life()
        assert manager.is_alive() is True
        manager.lose_life()
        assert manager.is_alive() is False
