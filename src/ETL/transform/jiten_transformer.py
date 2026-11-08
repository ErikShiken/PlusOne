"""Transformer for Jiten frequency list data."""

from src.ETL.transform.transform_base import TransformBase
from src.ETL.models import WordReading

class JitenTransformer(TransformBase[dict, WordReading]):
    """Transforms Jiten CSV rows into WordReading objects."""

    language = "ja"

    def transform(self, data_row: dict[str, str]) -> WordReading:
        """Convert a Jiten CSV row dictionary into a WordReading."""
        return WordReading(word=data_row["Word"], reading=data_row["Form"], frequency_rank=data_row["Rank"])
