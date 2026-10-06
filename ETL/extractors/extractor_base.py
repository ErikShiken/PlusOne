import codecs
from abc import ABC, abstractmethod
from typing import Iterator


class ExtractorBase(ABC):
    UTF8_BOM = codecs.BOM_UTF8
    encoding = "utf-8"

    @abstractmethod
    def extract(self, file_path:str) -> Iterator[dict[str, str]]:
        pass