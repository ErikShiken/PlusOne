"""Abstract base class for ETL loaders."""

from abc import ABC, abstractmethod
from typing import Iterable

from src.ETL.models import WordReading


class LoaderBase(ABC):
    """Base class for loaders that persist data to storage."""

    @abstractmethod
    def load(self, entries: Iterable[WordReading]) -> None:
        """Load the given entries into storage."""
