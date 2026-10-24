import json
from types import MappingProxyType
from typing import Iterable, Self
import re
from visitors.sentence_visitor import SentenceVisitor
from visitors.registry import HANDLERS, handles


PUNCTUATION = re.compile(r"[、。「」『』！？・]+")

def is_punctuation(token: str) -> bool:
    return bool(PUNCTUATION.fullmatch(token))

class JapaneseVisitor(SentenceVisitor):
    grammar = None

    def __init__(self, user_knowns: set[str]):
        self.unknowns: set[str] = set()
        self.user_known = user_knowns

    def visit(self, kind: str, item: str) -> bool:
        handler = HANDLERS[kind]
        return handler(self, item)

    def get_unknowns(self, sentence: Iterable[str]) -> set[str]:
        unknowns = set()
        for word in sentence:
            if is_punctuation(word):
                continue
            if not self.visit("vocabulary", word) and not self.visit("grammar", word):
                unknowns.add(word)
        return unknowns

    @handles("vocabulary")
    def visit_vocabulary(self, vocabulary: str) -> bool:
        return vocabulary in self.user_known

    @handles("grammar")
    def visit_grammar_rule(self, grammar_rule: str) -> bool:
        return grammar_rule in self.grammar

    def count_unknowns(self, item: str) -> None:
        if item not in self.user_known:
            self.unknowns.add(item)

    @staticmethod
    def read_user_known(user_known_file: str) -> set[str]:
        with open(user_known_file, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())

    @classmethod
    def set_grammar(cls, grammar_file: str) -> None:
        with open(grammar_file, "r", encoding="utf-8") as f:
            cls.grammar = MappingProxyType(json.load(f))

    @classmethod
    def from_file(cls, user_known_file: str) -> Self:
        return cls(cls.read_user_known(user_known_file))