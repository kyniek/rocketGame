import json
import tempfile
import os
from ..challenges.challenge_loader import ChallengeLoader


class TestChallengeLoader:
    """Tests for ChallengeLoader class."""

    def test_loader_loads_questions(self):
        """Should return list of challenges."""
        loader = ChallengeLoader()

        # Create temp JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([
                {"question": "2+2?", "answerA": "4", "answerB": "", "answerC": ""},
                {"question": "3+3?", "answerA": "6", "answerB": "", "answerC": ""}
            ], f)
            temp_path = f.name

        try:
            challenges = loader.load_from_json(temp_path)
            assert len(challenges) == 2
        finally:
            os.unlink(temp_path)

    def test_loader_creates_multiple_choice(self):
        """Should create MultipleChoiceChallenge when B and C are non-empty."""
        loader = ChallengeLoader()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([
                {"question": "Color?", "answerA": "blue", "answerB": "red", "answerC": "green"}
            ], f)
            temp_path = f.name

        try:
            challenges = loader.load_from_json(temp_path)
            assert len(challenges) == 1
            from challenges.challenge import MultipleChoiceChallenge
            assert isinstance(challenges[0], MultipleChoiceChallenge)
            assert challenges[0].options == ["blue", "red", "green"]
        finally:
            os.unlink(temp_path)

    def test_loader_creates_text_challenge(self):
        """Should create TextChallenge when B and C are empty."""
        loader = ChallengeLoader()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([
                {"question": "Capital?", "answerA": "Paris", "answerB": "", "answerC": ""}
            ], f)
            temp_path = f.name

        try:
            challenges = loader.load_from_json(temp_path)
            assert len(challenges) == 1
            from challenges.challenge import TextChallenge
            assert isinstance(challenges[0], TextChallenge)
        finally:
            os.unlink(temp_path)

    def test_loader_empty_file(self):
        """Should return empty list for empty JSON array."""
        loader = ChallengeLoader()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_path = f.name

        try:
            challenges = loader.load_from_json(temp_path)
            assert len(challenges) == 0
        finally:
            os.unlink(temp_path)
