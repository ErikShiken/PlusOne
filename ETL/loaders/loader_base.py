from abc import ABC, abstractmethod
from typing import Iterable

from ETL.models import Vocabulary, WordReading


class LoaderBase(ABC):
    @abstractmethod
    def load(self, entries: Iterable[WordReading]) -> None:
        pass