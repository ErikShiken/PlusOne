"""Abstract base class for ETL transformers."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

In = TypeVar("In")
Out = TypeVar("Out")


class TransformBase(ABC, Generic[In, Out]):
    """Base class for transformers that convert input data into output records."""

    @abstractmethod
    def transform(self, data: In) -> Out:
        """Transform the input data into the output form."""
