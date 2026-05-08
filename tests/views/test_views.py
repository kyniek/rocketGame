"""Tests for views - simplified to avoid arcade window requirements."""

import pytest
from unittest.mock import Mock, patch


def test_views_instantiate():
    """All views should be importable and have correct attributes."""
    # Import all views
    from views.start_view import StartView
    from views.challenge_view import ChallengeView
    from views.victory_view import VictoryView
    from views.game_over_view import GameOverView

    # Verify classes exist and have expected methods
    assert hasattr(StartView, 'on_show')
    assert hasattr(StartView, 'on_draw')
    assert hasattr(StartView, 'on_mouse_press')

    assert hasattr(ChallengeView, 'on_show')
    assert hasattr(ChallengeView, 'on_draw')
    assert hasattr(ChallengeView, 'on_key_press')

    assert hasattr(VictoryView, 'on_show')
    assert hasattr(VictoryView, 'on_draw')
    assert hasattr(VictoryView, 'on_mouse_press')

    assert hasattr(GameOverView, 'on_show')
    assert hasattr(GameOverView, 'on_draw')
    assert hasattr(GameOverView, 'on_mouse_press')


def test_challenge_view_attributes():
    """ChallengeView should store challenge and callback."""
    from views.challenge_view import ChallengeView
    from challenges.challenge import TextChallenge

    challenge = TextChallenge("Test?", "answer")
    callback = Mock()

    # We need to mock arcade.View.__init__ since ChallengeView calls super().__init__()
    with patch('arcade.View.__init__', return_value=None):
        view = ChallengeView(challenge, callback)
        assert view.challenge == challenge
        assert view.callback == callback


def test_victory_view_attributes():
    """VictoryView should store score and wrong answers."""
    from views.victory_view import VictoryView

    # Mock arcade.View.__init__
    with patch('arcade.View.__init__', return_value=None):
        view = VictoryView(score=42, wrong_answers=[{'q': 'a', 'u': 'b', 'c': 'c'}])
        assert view.score == 42
        assert len(view.wrong_answers) == 1


def test_game_over_view_attributes():
    """GameOverView should store score."""
    from views.game_over_view import GameOverView

    # Mock arcade.View.__init__
    with patch('arcade.View.__init__', return_value=None):
        view = GameOverView(score=10)
        assert view.score == 10


def test_start_view_has_expected_methods():
    """StartView should have expected methods for Arcade."""
    from views.start_view import StartView

    # Check class has required arcade view methods
    assert callable(getattr(StartView, 'on_show', None))
    assert callable(getattr(StartView, 'on_draw', None))
    assert callable(getattr(StartView, 'on_mouse_press', None))
