from typing import Iterable

from observability.log_mixin import LogMixin
from ETL.loaders.loader_base import LoaderBase
from ETL.models import WordReading

import sqlite3

from performance.clock_decorator import clock


class JitenLoader(LogMixin, LoaderBase):
    language = "ja"

    def __init__(self, conn: sqlite3.Connection, *, batch_limit: int = 1000):
        super().__init__()
        self.conn = conn
        self.batch_limit = batch_limit
        self.vocab_sql = "INSERT OR IGNORE INTO vocabulary (word) VALUES (?)"
        self.reading_sql = "INSERT OR IGNORE INTO readings (vocab_id, reading, frequency_rank) VALUES (?, ?, ?)"
        self.find_word = "SELECT id FROM vocabulary WHERE word = ?"

    @clock
    def load(self, entries: Iterable[WordReading]) -> None:
        self.log("Loading entries")
        ids = {}
        batch = []
        for entry in entries:
            if entry.word not in ids:
                unused_cursor = self.conn.execute(self.vocab_sql, (entry.word,))
                cursor = self.conn.execute(self.find_word, (entry.word,))
                ids[entry.word] = cursor.fetchone()[0]
            batch.append((ids[entry.word], entry.reading, entry.frequency_rank))
            if len(batch) >= self.batch_limit:
                self.conn.executemany(self.reading_sql, batch)
                batch = []

        if batch:
            self.conn.executemany(self.reading_sql, batch)

        self.conn.commit()
        self.log(f"load finished: {len(ids)} words")

    def __repr__(self) -> str:
        class_name = type(self).__name__
        return f"{class_name}(batch_limit={self.batch_limit!r})"
