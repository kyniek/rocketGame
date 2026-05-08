import random
from typing import List

from challenges.challenge import Challenge


class ChallengeManager:
    """Manages challenge presentation and scoring."""

    def __init__(self, questions_file: str):
        """Initialize with questions from JSON file.

        Args:
            questions_file: Path to the questions JSON file.
        """
        self.challenges: List[Challenge] = []
        self.wrong_answers: List[dict] = []
        self._load_questions(questions_file)

    def _load_questions(self, filepath: str) -> None:
        """Load questions from JSON file."""
        try:
            from challenges.challenge_loader import ChallengeLoader
            loader = ChallengeLoader()
            self.challenges = loader.load_from_json(filepath)
        except FileNotFoundError:
            self.challenges = []

    def get_random_challenge(self) -> Challenge:
        """Get a random challenge from the list.

        Returns:
            A random Challenge object.
        """
        if not self.challenges:
            # Return a default challenge
            from challenges.challenge import TextChallenge
            return TextChallenge("Default question", "default")
        return random.choice(self.challenges)

    def all_questions_answered_correctly(self) -> bool:
        """Check if all questions have been answered correctly.

        Returns:
            True if no challenges remain (all answered correctly), False otherwise.
        """
        return len(self.challenges) == 0
