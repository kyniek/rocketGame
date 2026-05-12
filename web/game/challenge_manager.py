import random
from typing import List

from .challenge import Challenge


class ChallengeManager:
    """Manages challenge presentation and scoring."""

    def __init__(self, questions_file: str):
        """Initialize with questions from JSON file."""
        self.challenges: List[Challenge] = []
        self.wrong_answers: List[dict] = []
        self._load_questions(questions_file)

    def _load_questions(self, filepath: str) -> None:
        """Load questions from JSON file."""
        try:
            from .challenge_loader import ChallengeLoader
            loader = ChallengeLoader()
            self.challenges = loader.load_from_json(filepath)
        except FileNotFoundError:
            self.challenges = []

    def get_random_challenge(self) -> Challenge:
        """Get a random challenge from the list."""
        if not self.challenges:
            from .challenge import TextChallenge
            return TextChallenge("Default question", "default")
        return random.choice(self.challenges)

    def all_questions_answered_correctly(self) -> bool:
        """Check if all questions have been answered correctly."""
        return len(self.challenges) == 0
