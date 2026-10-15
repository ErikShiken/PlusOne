

class DifficultyClassifier:
    @staticmethod
    def classify(unseen: set[str]) -> str:
        match list(unseen):
            case []:
                return "known"
            case [only]:
                return f"n+1 (new: {only})"
            case [*rest]:
                return f"unknown (new: {rest})"