"""Data models for the ETL pipeline.

This module defines dataclasses and named tuples used to represent
vocabulary, readings, and word understanding throughout the pipeline.
"""

from __future__ import annotations

from collections.abc import Sequence, Iterable

from dataclasses import dataclass

from typing import NamedTuple


@dataclass
class Vocabulary:
    """Represents a vocabulary entry with its word and reading."""
    word: str
    reading: str
    id: int | None = None
    synonym_id: int | None = None

class VocabRow(NamedTuple):
    """Database row representation for vocabulary entries."""
    id: int
    word: str
    synonym_id: int | None

@dataclass
class WordReading:
    """Represents a word with its reading and frequency rank."""
    word: str
    reading: str
    frequency_rank: int

    def __post_init__(self) -> None:
        self.frequency_rank = int(self.frequency_rank)

@dataclass
class WordUnderstanding:
    """Represents a word and whether the user knows it."""
    word: str
    known: bool


@dataclass
class Reading:
    """Represents a reading associated with a vocabulary entry."""
    vocab_id: int
    reading: str
    frequency_rank: int
    id: int | None = None

    def __post_init__(self) -> None:
        self.frequency_rank = int(self.frequency_rank)

class ReadingRow(NamedTuple):
    """Database row representation for readings."""
    id: int
    vocab_id: int
    reading: str
    frequency_rank: int | None