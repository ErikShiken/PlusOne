from abc import ABC, abstractmethod


class TransformBase(ABC):
    @abstractmethod
    def transform(self, data_row:dict):
        pass