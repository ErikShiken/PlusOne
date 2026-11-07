from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")

class ExtractorBase(ABC, Generic[T]):
    @abstractmethod
    def extract(self) -> T:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass