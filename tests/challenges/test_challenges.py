import pytest
from ..challenges.challenge import Challenge, MultipleChoiceChallenge, TextChallenge


class TestMultipleChoiceChallenge:
    """Tests for MultipleChoiceChallenge."""

    def test_multiple_choice_check_correct(self):
        """Correct answer should pass."""
        challenge = MultipleChoiceChallenge(
            question="2+2?",
            correct_answer="4",
            options=["4", "3", "5"]
        )
        assert challenge.check_answer("4") is True

    def test_multiple_choice_check_incorrect(self):
        """Wrong answer should fail."""
        challenge = MultipleChoiceChallenge(
            question="2+2?",
            correct_answer="4",
            options=["4", "3", "5"]
        )
        assert challenge.check_answer("3") is False
        assert challenge.check_answer("5") is False

    def test_multiple_choice_case_insensitive(self):
        """Should be case-insensitive."""
        challenge = MultipleChoiceChallenge(
            question="Color?",
            correct_answer="Blue",
            options=["Blue", "Red", "Green"]
        )
        assert challenge.check_answer("blue") is True
        assert challenge.check_answer("BLUE") is True

    def test_multiple_choice_whitespace_trim(self):
        """Should trim whitespace."""
        challenge = MultipleChoiceChallenge(
            question="Color?",
            correct_answer="blue",
            options=["blue", "red", "green"]
        )
        assert challenge.check_answer("  blue  ") is True


class TestTextChallenge:
    """Tests for TextChallenge."""

    def test_text_challenge_case_insensitive(self):
        """Should be case-insensitive."""
        challenge = TextChallenge(
            question="Sky color?",
            correct_answer="Blue"
        )
        assert challenge.check_answer("blue") is True
        assert challenge.check_answer("BLUE") is True

    def test_text_challenge_whitespace_trim(self):
        """Should trim whitespace."""
        challenge = TextChallenge(
            question="Sky color?",
            correct_answer="blue"
        )
        assert challenge.check_answer("  blue  ") is True

    def test_text_challenge_check_correct(self):
        """Correct answer should pass."""
        challenge = TextChallenge(
            question="Capital of France?",
            correct_answer="Paris"
        )
        assert challenge.check_answer("Paris") is True

    def test_text_challenge_check_incorrect(self):
        """Wrong answer should fail."""
        challenge = TextChallenge(
            question="Capital of France?",
            correct_answer="Paris"
        )
        assert challenge.check_answer("London") is False


class TestChallengeBase:
    """Tests for Challenge base class."""

    def test_challenge_base_abstract(self):
        """Should not be able to instantiate abstract base class."""
        with pytest.raises(TypeError):
            Challenge("Test", "answer")
