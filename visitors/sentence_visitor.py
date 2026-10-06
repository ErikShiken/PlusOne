from abc import ABC, abstractmethod

class SentenceVisitor(ABC):
    @abstractmethod
    def visit_vocabulary(self, vocabulary: str) -> None:
        pass

    @abstractmethod
    def visit_grammar_rule(self, grammar_rule: str) -> None:
        pass
