import json
from typing import List

from .challenge import Challenge, MultipleChoiceChallenge, TextChallenge


class ChallengeLoader:
    """Loads challenges from a JSON file."""

    def load_from_json(self, filepath: str) -> List[Challenge]:
        """Load challenges from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        challenges = []
        for item in data:
            question = item.get('question', '')
            answer_a = item.get('answerA', '')
            answer_b = item.get('answerB', '')
            answer_c = item.get('answerC', '')

            if not answer_b.strip() and not answer_c.strip():
                challenge = TextChallenge(question, answer_a)
            else:
                options = [answer_a, answer_b, answer_c]
                challenge = MultipleChoiceChallenge(question, answer_a, options)

            challenges.append(challenge)

        return challenges
