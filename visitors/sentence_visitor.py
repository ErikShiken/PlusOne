"""Abstract base class for sentence visitors that identify unknown tokens."""

from abc import ABC, abstractmethod
from typing import Iterable


class SentenceVisitor(ABC):
    """Base class for visitors that check sentence tokens against known data."""

    @abstractmethod
    def visit_vocabulary(self, vocabulary: str) -> None:
        """Handle a vocabulary token."""

    @abstractmethod
    def visit_grammar_rule(self, grammar_rule: str) -> None:
        """Handle a grammar rule token."""

    @abstractmethod
    def get_unknowns(self, sentence: Iterable[str]):
        """Return the set of tokens in the sentence that are unknown."""
