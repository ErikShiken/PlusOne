from ETL.transform.transform_base import TransformBase
from ETL.models import WordReading

class JitenTransformer(TransformBase):
    language = "ja"
    def transform(self, data_row: dict) -> WordReading:
        return WordReading(word=data_row["Word"], reading=data_row["Form"], frequency_rank=data_row["Rank"])