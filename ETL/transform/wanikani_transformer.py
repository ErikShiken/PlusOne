"""Transformer that converts Wanikani word-stage data into WordUnderstanding records."""

from typing import Mapping

from ETL.transform.transform_base import TransformBase
from ETL.models import WordUnderstanding


class WanikaniTransformer(TransformBase[Mapping[str, str], list[WordUnderstanding]]):
    """Marks words as known when their Wanikani stage is 8 or higher."""

    language = "ja"

    def transform(self, data: Mapping[str, str]) -> list[WordUnderstanding]:
        """Convert a word-to-stage mapping into WordUnderstanding objects."""
        return [
            WordUnderstanding(word=word, known=int(stage) >= 8)
            for word, stage in data.items()
            if "\u301c" not in word
        ]
    