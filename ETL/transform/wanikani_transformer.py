from typing import Mapping

from ETL.transform.transform_base import TransformBase
from ETL.models import WordUnderstanding

class WanikaniTransformer(TransformBase[Mapping[str, str], list[WordUnderstanding]]):
    language = "ja"
    def transform(self, data: Mapping[str, str]) -> list[WordUnderstanding]:
        return [
            WordUnderstanding(word=word, known=int(stage) >= 8)
            for word, stage in data.items()
            if "\u301c" not in word
        ]