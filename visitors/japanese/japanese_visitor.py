"""Japanese sentence visitor that identifies unknown vocabulary and grammar."""

import json
from types import MappingProxyType
from typing import Iterable, Self, Mapping, Any
import re
from visitors.sentence_visitor import SentenceVisitor
from visitors.registry import HANDLERS, handles


PUNCTUATION = re.compile(r"[、。「」『』！？・]+")

def is_punctuation(token: str) -> bool:
    """Return True if the token consists solely of Japanese punctuation."""
    return bool(PUNCTUATION.fullmatch(token))

class JapaneseVisitor(SentenceVisitor):
    """Visitor that checks Japanese tokens against known vocabulary and grammar."""

    grammar: Mapping[str, Any] = MappingProxyType({})

    def __init__(self, user_knowns: set[str]):
        """Initialize with the set of words the user already knows."""
        self.unknowns: set[str] = set()
        self.user_known = user_knowns

    def visit(self, kind: str, item: str) -> bool:
        """Dispatch the item to the handler registered for the given kind."""
        handler = HANDLERS[kind]
        return handler(self, item)

    def get_unknowns(self, sentence: Iterable[str]) -> set[str]:
        """Return the set of tokens in the sentence that are neither
        known vocabulary nor grammar."""
        unknowns = set()
        for word in sentence:
            if is_punctuation(word):
                continue
            if (not self.visit("vocabulary", word) and
                    not self.visit("grammar", word)):
                unknowns.add(word)
        return unknowns

    @handles("vocabulary")
    def visit_vocabulary(self, vocabulary: str) -> bool:
        """Return True if the vocabulary item is in the user's known words."""
        return vocabulary in self.user_known

    @handles("grammar")
    def visit_grammar_rule(self, grammar_rule: str) -> bool:
        """Return True if the grammar rule is in the loaded grammar table."""
        return grammar_rule in self.grammar

    def count_unknowns(self, item: str) -> None:
        """Add the item to the unknowns set if it is not a known word."""
        if item not in self.user_known:
            self.unknowns.add(item)

    @staticmethod
    def read_user_known(user_known_file: str) -> set[str]:
        """Read a newline-separated file of known words into a set."""
        with open(user_known_file, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())

    @classmethod
    def set_grammar(cls, grammar_file: str) -> None:
        """Load the grammar table from a JSON file into an immutable mapping."""
        with open(grammar_file, "r", encoding="utf-8") as f:
            cls.grammar = MappingProxyType(json.load(f))

    @classmethod
    def from_file(cls, user_known_file: str) -> Self:
        """Construct a JapaneseVisitor from a file of known words."""
        return cls(cls.read_user_known(user_known_file))
