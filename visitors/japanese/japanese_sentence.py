import json
from types import MappingProxyType

from visitors.sentence_visitor import SentenceVisitor
from unknown_exception import UnknownException

class JapaneseSentence(SentenceVisitor):
    grammar = None

    def __init__(self, user_knowns):
        self.unknowns = set()
        self.user_known = user_knowns

    def visit_vocabulary(self, vocabulary):
        self.count_unknowns(vocabulary)

    def visit_grammar_rule(self, grammar_rule):
        self.count_unknowns(grammar_rule)

    def count_unknowns(self, item):
        if item not in self.user_known:
            self.unknowns.add(item)

        if len(self.unknowns) > 1:
            raise UnknownException(self.unknowns)

    @staticmethod
    def read_user_known():
        with open("user_known.dat", "r", encoding="utf-8") as f:
            return set(f.read().splitlines())

    @classmethod
    def set_grammar(cls, grammar_file):
        with open(grammar_file, "r", encoding="utf-8") as f:
            cls.grammar = MappingProxyType(json.load(f))