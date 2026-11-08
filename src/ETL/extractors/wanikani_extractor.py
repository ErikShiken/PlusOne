"""Extractor for Wanikani API data."""

from typing import Mapping, Callable

from src.ETL.extractors.extractor_base import ExtractorBase
import os
import requests

class WanikaniExtractor(ExtractorBase[Mapping[str, str]]):
    """Extracts vocabulary and SRS assignment data from the Wanikani API."""

    language = "ja"
    update_filter = "&updated_after="
    assignments_url = "https://api.wanikani.com/v2/assignments?subject_types=vocabulary,kana_vocabulary"
    subjects_web_query = "https://api.wanikani.com/v2/subjects?types=vocabulary,kana_vocabulary"

    def __init__(self, last_assignment_update_time: str | None = None,
                 last_subject_update_time: str | None = None):
        """Initialize with optional last update timestamps for incremental sync."""
        self.token = os.environ["WANIKANI_TOKEN"]
        self.headers = {
            "Wanikani-Revision": "20170710",
            "Authorization": f"Bearer {self.token}",
        }
        self.last_assignment_update_time = last_assignment_update_time
        self.last_subject_update_time = last_subject_update_time

    def extract(self) -> Mapping[str, str]:
        """Extract and combine subject and assignment data into a word-to-stage mapping."""
        subject_table, subject_update_time = self._get_data(self.assignments_url, self._assignment_pair,
                                                            self.last_assignment_update_time)
        mapping_table, mapping_update_time = self._get_data(self.subjects_web_query, self._subject_pair,
                                                            self.last_subject_update_time)
        return {mapping_table[subject_id]: stage for subject_id, stage in subject_table.items()}

    def extract_subjects(self) -> tuple[Mapping[str, str], str | None]:
        """Extract subject data, returning a mapping and the update timestamp."""
        return self._get_data(self.subjects_web_query, self._subject_pair, self.last_subject_update_time)

    def extract_assignments(self) -> tuple[Mapping[str, str], str | None]:
        """Extract assignment data, returning a mapping and the update timestamp."""
        return self._get_data(self.assignments_url, self._assignment_pair, self.last_assignment_update_time)

    @staticmethod
    def _assignment_pair(item):
        """Extract (subject_id, srs_stage) from an assignment API item."""
        return item['data']['subject_id'], item['data']['srs_stage']

    @staticmethod
    def _subject_pair(item):
        """Extract (id, characters) from a subject API item."""
        return item['id'], item['data']['characters']

    def _get_data(self, url: str, pair_func : Callable[[dict], tuple[str, str]], last_update_time: str | None) -> tuple[Mapping[str, str], str | None]:
        """Fetch paginated data from the Wanikani API."""
        data = {}
        last_update = None
        this_update_filter = None
        if last_update_time:
            this_update_filter = self.update_filter + last_update_time

        if last_update_time and url:
            url += this_update_filter

        while url is not None:
            r = requests.get(url, headers=self.headers)
            match r.json():
                case {"data": items, "pages": {"next_url": url}}:
                    if not last_update:
                        last_update = r.json()["data_updated_at"]
                    data.update({pair_func(item) for item in items})
                case {"error": message, "code": code}:
                    raise RuntimeError(f"Wanikani API error: {message}, code: {code}")
                case _:
                    raise RuntimeError(f"unexpected reply: {r.json()}")

        return data, last_update
