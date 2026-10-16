class DifficultyClassifier:
    @staticmethod
    def classify(unseen: set[str]) -> str:
        match list(unseen):
            case []:
                return "known"
            case [*rest]:
                return f"n+{len(rest)}"