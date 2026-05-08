import json
import tempfile
import os
from managers.challenge_manager import ChallengeManager


class TestChallengeManager:
    """Tests for ChallengeManager class."""

    def test_manager_loads_challenges(self):
        """Should load challenges from JSON file."""
        # Create temp JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([
                {"question": "2+2?", "answerA": "4", "answerB": "", "answerC": ""}
            ], f)
            temp_path = f.name

        try:
            manager = ChallengeManager(temp_path)
            assert len(manager.challenges) == 1
        finally:
            os.unlink(temp_path)

    def test_manager_get_random_challenge(self):
        """Should return a random challenge from the list."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([
                {"question": "Color?", "answerA": "blue", "answerB": "", "answerC": ""},
                {"question": "Shape?", "answerA": "circle", "answerB": "", "answerC": ""}
            ], f)
            temp_path = f.name

        try:
            manager = ChallengeManager(temp_path)

            # Get random challenge
            challenge = manager.get_random_challenge()

            assert challenge is not None
            assert challenge.question in ["Color?", "Shape?"]
        finally:
            os.unlink(temp_path)

    def test_manager_empty_file(self):
        """Should handle empty questions file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_path = f.name

        try:
            manager = ChallengeManager(temp_path)
            assert len(manager.challenges) == 0
        finally:
            os.unlink(temp_path)

    def test_manager_all_questions_answered_correctly(self):
        """Should return True when all questions are answered."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([
                {"question": "2+2?", "answerA": "4", "answerB": "", "answerC": ""}
            ], f)
            temp_path = f.name

        try:
            manager = ChallengeManager(temp_path)
            # Initially not all answered
            assert manager.all_questions_answered_correctly() is False

            # Remove the challenge to simulate all answered
            manager.challenges = []
            assert manager.all_questions_answered_correctly() is True
        finally:
            os.unlink(temp_path)
