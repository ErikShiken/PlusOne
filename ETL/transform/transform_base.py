from abc import ABC, abstractmethod
from typing import TypeVar, Generic

In = TypeVar("In")
Out = TypeVar("Out")

class TransformBase(ABC, Generic[In, Out]):
    @abstractmethod
    def transform(self, data:In) -> Out:
        pass