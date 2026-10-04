from abc import ABC, abstractmethod
from typing import Iterable

from ETL.models import Vocabulary


class LoaderBase(ABC):
    @abstractmethod
    def load(self, entries: Iterable[Vocabulary]):
        pass