"""Extractor for Jiten frequency list data."""

from typing import Iterator

from src.ETL.extractors.extractor_base import ExtractorBase
import codecs
import csv

class JitenExtractor(ExtractorBase[Iterator[dict[str, str]]]):
    """Extracts vocabulary data from a Jiten frequency list CSV file."""

    language = "ja"
    UTF8_BOM = codecs.BOM_UTF8
    encoding = "utf-8"

    def __init__(self, file_path: str):
        """Initialize with the path to the frequency list CSV file."""
        self.file_path = file_path

    def extract(self) -> Iterator[dict[str, str]]:
        """Yield rows from the CSV file as dictionaries."""
        with open(self.file_path, "rb") as f:
            first_three = f.read(3)
            if first_three == self.UTF8_BOM:
                self.encoding = "utf-8-sig"

        with open(self.file_path, "r", encoding=self.encoding) as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row