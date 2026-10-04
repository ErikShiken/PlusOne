import codecs
from abc import ABC, abstractmethod


class ExtractorBase(ABC):
    UTF8_BOM = codecs.BOM_UTF8
    encoding = "utf-8"

    @abstractmethod
    def extract(self, file_path:str):
        pass