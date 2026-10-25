from typing import Mapping, Callable

from ETL.extractors.extractor_base import ExtractorBase
import os
import requests

class WanikaniExtractor(ExtractorBase[Mapping[str, str]]):
    language = "ja"
    assignments_url = "https://api.wanikani.com/v2/assignments?subject_types=vocabulary,kana_vocabulary"
    subjects_web_query = "https://api.wanikani.com/v2/subjects?types=vocabulary,kana_vocabulary"
    def __init__(self):
        self.token = os.environ["WANIKANI_TOKEN"]
        self.headers = {
            "Wanikani-Revision": "20170710",
            "Authorization": f"Bearer {self.token}",
        }

    def extract(self) -> Mapping[str, str]:
        subject_table = self._get_data(self.assignments_url, self._assignment_pair)
        mapping_table = self._get_data(self.subjects_web_query, self._subject_pair)
        return {mapping_table[subject_id]: stage for subject_id, stage in subject_table.items()}

    @staticmethod
    def _assignment_pair(item):
        return item['data']['subject_id'], item['data']['srs_stage']

    @staticmethod
    def _subject_pair(item):
        return item['id'], item['data']['characters']

    def _get_data(self, url: str, pair_func : Callable[[dict], tuple[str, str]]) -> Mapping[str, str]:
        data = {}
        while url is not None:
            r = requests.get(url, headers=self.headers)
            match r.json():
                case {"data": items, "pages": {"next_url": url}}:
                    data.update({pair_func(item) for item in items})
                case {"error": message, "code": code}:
                    raise RuntimeError(f"Wanikani API error: {message}, code: {code}")
                case _:
                    raise RuntimeError(f"unexpected reply: {r.json()}")

        return data