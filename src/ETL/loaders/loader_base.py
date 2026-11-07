from abc import ABC, abstractmethod
from typing import Iterable

from src.ETL.models import WordReading


class LoaderBase(ABC):
    @abstractmethod
    def load(self, entries: Iterable[WordReading]) -> None:
        pass