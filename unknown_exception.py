class UnknownException(Exception):
    """Raised when a sentence contains more than one unknown item in a sentence.
    An item is either a vocabulary word or a grammar rule."""

    def __init__(self, number_of_unknowns):
        super().__init__(f"{number_of_unknowns} unknowns found in the sentence.")
