import json
from types import MappingProxyType

from visitors.sentence_visitor import SentenceVisitor
from unknown_exception import UnknownException

class JapaneseSentence(SentenceVisitor):
    grammar = None

    def __init__(self, user_knowns: set[str]):
        self.unknowns: set[str] = set()
        self.user_known = user_knowns

    def visit_vocabulary(self, vocabulary: str) -> None:
        self.count_unknowns(vocabulary)

    def visit_grammar_rule(self, grammar_rule: str) -> None:
        self.count_unknowns(grammar_rule)

    def count_unknowns(self, item: str) -> None:
        if item not in self.user_known:
            self.unknowns.add(item)

        num_unknowns = len(self.unknowns)
        if num_unknowns > 1:
            raise UnknownException(num_unknowns)

    @staticmethod
    def read_user_known() -> set[str]:
        with open("user_known.dat", "r", encoding="utf-8") as f:
            return set(f.read().splitlines())

    @classmethod
    def set_grammar(cls, grammar_file: str) -> None:
        with open(grammar_file, "r", encoding="utf-8") as f:
            cls.grammar = MappingProxyType(json.load(f))