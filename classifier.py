from collections.abc import Sequence


class DifficultyClassifier:
    @staticmethod
    def classify(unseen: Sequence[str]) -> str:
        match unseen:
            case []:
                return "known"
            case [only]:
                return f"n+1 (new: {only})"
            case [*rest]:
                return f"unknown (new: {rest})"