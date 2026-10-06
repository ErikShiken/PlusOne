from abc import ABC, abstractmethod
from ETL.models import WordReading

class TransformBase(ABC):
    @abstractmethod
    def transform(self, data_row:dict) -> WordReading:
        pass