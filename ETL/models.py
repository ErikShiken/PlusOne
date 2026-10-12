from collections.abc import Sequence

from dataclasses import dataclass

from typing import NamedTuple


@dataclass
class Vocabulary:
    word: str
    reading: str
    id: int | None = None
    synonym_id: int | None = None

class VocabRow(NamedTuple):
    id: int
    word: str
    synonym_id: int | None

@dataclass
class WordReading:
    word: str
    reading: str
    frequency_rank: int

    def __post_init__(self) -> None:
        self.frequency_rank = int(self.frequency_rank)

@dataclass
class Reading:
    vocab_id: int
    reading: str
    frequency_rank: int
    id: int | None = None

    def __post_init__(self) -> None:
        self.frequency_rank = int(self.frequency_rank)

class ReadingRow(NamedTuple):
    id: int
    vocab_id: int
    reading: str
    frequency_rank: int | None

@dataclass
class Sentence(Sequence[str]):
    def __init__(self, words: list[str]):
        self._words = list(words)

    def __len__(self) -> int:
        return len(self._words)

    def __repr__(self) -> str:
        return f"Sentence({self._words!r})"

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Sentence(self._words[key])
        return self._words[key]

    def __contains__(self, word: str) -> bool:
        return word in self._words

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Sentence):
            return NotImplemented
        return self._words == other._words

    def __hash__(self) -> int:
        return hash(tuple(self._words))