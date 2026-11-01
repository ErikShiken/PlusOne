import logging
import time
import urllib.request
from collections.abc import Mapping
from pathlib import Path
from urllib.robotparser import RobotFileParser
from datetime import datetime

from ETL.extractors.extractor_base import ExtractorBase

logging.basicConfig(level=logging.DEBUG)

# a prototype to learn about web crawlers
def write_to_file(file_path: str, content: str):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d_%H%M%S")
    with open(f"{file_path}_{current_time}", "w", encoding="utf-8") as f:
        f.write(content)

_AGENT = "PlusOne/1.0 (+https://github.com/ErikShiken/PlusOne)"
_CRAWLER_HEADER = {
        "User-Agent": _AGENT
    }
_URL = "https://downloads.tatoeba.org/"
_TARGET = "jpn_sentences.tsv.bz2"
_DOWNLOAD_URL = f"{_URL}exports/per_language/jpn/"
_DOWNLOADED_FILE_NAME = "output_file.tsv.bz2"
_DOWNLOADED_FILE_PATH = Path(f"data/{_DOWNLOADED_FILE_NAME}")
class TatoebaExtractor(ExtractorBase[Mapping[str, str]]):
    language = "ja"
    _crawl_delay = 0
    _downloads_allowed = None
    _last_request = None

    def __init__(self):
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{_URL}robots.txt")
        rp.read()
        self._downloads_allowed = rp.can_fetch(_AGENT, _DOWNLOAD_URL)
        if not self._downloads_allowed:
            raise Exception("Downloads not allowed")
        if rp.crawl_delay(_AGENT):
            self._crawl_delay = int(rp.crawl_delay(_AGENT))
        self._last_request = time.monotonic()

    def extract(self) -> Mapping[Path, str]:
        if not _DOWNLOADED_FILE_PATH.is_file():
            remaining = self._crawl_delay - (time.monotonic() - self._last_request)
            if remaining > 0:
                time.sleep(remaining)
            req = urllib.request.Request(_DOWNLOAD_URL + _TARGET, headers=_CRAWLER_HEADER)
            response = urllib.request.urlopen(req)
            self._last_request = time.monotonic()
            _DOWNLOADED_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(_DOWNLOADED_FILE_PATH, "wb") as file:
                file.write(response.read())
            status = {_DOWNLOADED_FILE_PATH : "success"}
        else:
            status = {_DOWNLOADED_FILE_PATH : f"file @ {_DOWNLOADED_FILE_PATH}"}
        return status

if __name__ == '__main__':
    tatoeba_extractor = TatoebaExtractor()
    download_status = tatoeba_extractor.extract()
    print("download_status ", download_status)

