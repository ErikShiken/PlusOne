from abc import ABC, abstractmethod

class SentenceVisitor(ABC):
    @abstractmethod
    def visit_vocabulary(self, vocabulary):
        pass

    @abstractmethod
    def visit_grammar_rule(self, grammar_rule):
        pass
