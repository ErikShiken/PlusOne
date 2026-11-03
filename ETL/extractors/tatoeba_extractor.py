import bz2
import logging
import time
import urllib.request
from collections.abc import Generator
from pathlib import Path
from urllib.robotparser import RobotFileParser

from ETL.extractors.extractor_base import ExtractorBase

logging.basicConfig(level=logging.DEBUG)

# a prototype to learn about web crawlers
_AGENT = "PlusOne/1.0 (+https://github.com/ErikShiken/PlusOne)"
_CRAWLER_HEADER = {
        "User-Agent": _AGENT
    }
_URL = "https://downloads.tatoeba.org/"
_TARGET = "jpn_sentences.tsv.bz2"
_DOWNLOAD_URL = f"{_URL}exports/per_language/jpn/"
_DOWNLOADED_FILE_NAME = "output_file.tsv.bz2"
_DOWNLOADED_FILE_PATH = Path(__file__).parents[2] / "data" / _DOWNLOADED_FILE_NAME

class TatoebaExtractor(ExtractorBase[Generator[str]]):
    language = "ja"
    _crawl_delay = 0
    _downloads_allowed = None
    _last_request = None

    def __enter__(self):
        rp = RobotFileParser()
        rp.set_url(f"{_URL}robots.txt")
        rp.read()
        self._downloads_allowed = rp.can_fetch(_AGENT, _DOWNLOAD_URL)
        if not self._downloads_allowed:
            raise PermissionError("Downloads not allowed")

        crawl_delay = rp.crawl_delay(_AGENT)
        if crawl_delay:
            self._crawl_delay = int(crawl_delay)
        self._last_request = time.monotonic()

        if not _DOWNLOADED_FILE_PATH.is_file():
            self._download_file()

        self._file = bz2.open(_DOWNLOADED_FILE_PATH, "rt", encoding="utf-8")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()

    def extract(self) -> Generator[str]:
        for entry in self._file:
            columns = entry.strip().split("\t")
            yield columns[-1]

    def _download_file(self):
        remaining = self._crawl_delay - (time.monotonic() - self._last_request)
        if remaining > 0:
            time.sleep(remaining)
        req = urllib.request.Request(_DOWNLOAD_URL + _TARGET, headers=_CRAWLER_HEADER)
        with urllib.request.urlopen(req) as response:
            self._last_request = time.monotonic()
            _DOWNLOADED_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(_DOWNLOADED_FILE_PATH, "wb") as file:
                file.write(response.read())
