from abc import ABC, abstractmethod


class Challenge(ABC):
    """Abstract base class for challenges."""

    def __init__(self, question: str, correct_answer: str):
        """Initialize challenge.

        Args:
            question: The question text.
            correct_answer: The correct answer string.
        """
        self.question = question
        self.correct_answer = correct_answer

    @abstractmethod
    def check_answer(self, user_input: str) -> bool:
        """Check if the answer is correct.

        Args:
            user_input: The user's answer.

        Returns:
            True if correct, False otherwise.
        """
        pass


class MultipleChoiceChallenge(Challenge):
    """Multiple choice challenge with options."""

    def __init__(self, question: str, correct_answer: str, options: list[str]):
        """Initialize multiple choice challenge.

        Args:
            question: The question text.
            correct_answer: The correct answer (first option).
            options: List of 3 options [answerA, answerB, answerC].
        """
        super().__init__(question, correct_answer)
        self.options = options

    def check_answer(self, user_input: str) -> bool:
        """Check answer against correct answer (case-insensitive, trimmed)."""
        normalized_user = user_input.strip().lower()
        normalized_correct = self.correct_answer.strip().lower()
        return normalized_user == normalized_correct


class TextChallenge(Challenge):
    """Text-based challenge where user types the answer."""

    def check_answer(self, user_input: str) -> bool:
        """Check answer (case-insensitive, trimmed)."""
        normalized_user = user_input.strip().lower()
        normalized_correct = self.correct_answer.strip().lower()
        return normalized_user == normalized_correct
