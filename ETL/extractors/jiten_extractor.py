from ETL.extractors.extractor_base import ExtractorBase
import csv

class JitenExtractor(ExtractorBase):
    language = "ja"
    def extract(self, file_path: str):
        with open(file_path, "rb") as f:
            first_three = f.read(3)
            if first_three == self.UTF8_BOM:
                self.encoding = "utf-8-sig"

        with open(file_path, "r", encoding=self.encoding) as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row