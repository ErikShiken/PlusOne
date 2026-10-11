import json
from types import MappingProxyType
from typing import Callable, Self

from visitors.sentence_visitor import SentenceVisitor
from visitors.registry import HANDLERS, handles

class JapaneseSentence(SentenceVisitor):
    grammar = None

    def __init__(self, user_knowns: set[str], unknown_rule: Callable[[set[str]], None]):
        self.unknowns: set[str] = set()
        self.user_known = user_knowns
        self.unknown_rule = unknown_rule

    def visit(self, kind: str, item: str) -> None:
        handler = HANDLERS[kind]
        handler(self, item)

    @handles("vocabulary")
    def visit_vocabulary(self, vocabulary: str) -> None:
        self.count_unknowns(vocabulary)

    @handles("grammar")
    def visit_grammar_rule(self, grammar_rule: str) -> None:
        self.count_unknowns(grammar_rule)

    def count_unknowns(self, item: str) -> None:
        if item not in self.user_known:
            self.unknowns.add(item)

        self.unknown_rule(self.unknowns)

    @staticmethod
    def read_user_known(user_known_file: str) -> set[str]:
        with open(user_known_file, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())

    @classmethod
    def set_grammar(cls, grammar_file: str) -> None:
        with open(grammar_file, "r", encoding="utf-8") as f:
            cls.grammar = MappingProxyType(json.load(f))

    @classmethod
    def from_file(cls, user_known_file: str, unknown_rule: Callable[[set[str]], None]) -> Self:
        return cls(cls.read_user_known(user_known_file), unknown_rule)