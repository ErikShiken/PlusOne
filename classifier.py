"""Difficulty classification for unseen vocabulary.

Provides a simple heuristic that scores difficulty based on the number of
unseen words in a sentence.
"""


class DifficultyClassifier:
    """Classifies sentence difficulty using a simple unseen-word heuristic."""

    @staticmethod
    def classify(unseen: set[str]) -> int:
        """Return a difficulty score equal to the number of unseen words."""
        return len(unseen)
