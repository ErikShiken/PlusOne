class DifficultyClassifier:
    @staticmethod
    def classify(unseen: set[str]) -> int:
        return len(unseen)