from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TypeVar, Generic

T = TypeVar("T")

@contextmanager
class ExtractorBase(ABC, Generic[T]):
    @abstractmethod
    def extract(self) -> T:
        pass

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass