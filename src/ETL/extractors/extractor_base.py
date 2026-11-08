"""Abstract base class for ETL extractors."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")

class ExtractorBase(ABC, Generic[T]):
    """Base class for extractors that pull data from external sources."""

    @abstractmethod
    def extract(self) -> T:
        """Extract and return data from the source."""
        pass

    def __enter__(self):
        """Enter the context manager, returning self."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager, cleaning up resources."""
        pass