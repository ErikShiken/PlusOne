from abc import ABC, abstractmethod
from typing import Iterable

class SentenceVisitor(ABC):
    @abstractmethod
    def visit_vocabulary(self, vocabulary: str) -> None:
        pass

    @abstractmethod
    def visit_grammar_rule(self, grammar_rule: str) -> None:
        pass

    @abstractmethod
    def get_unknowns(self, sentence: Iterable[str]):
        pass