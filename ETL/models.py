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