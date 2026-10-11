from typing import Iterable

from performance.clock_decorator import clock
from ETL.loaders.loader_base import LoaderBase
from ETL.models import WordReading

import sqlite3

from performance.clock_decorator import clock


class JitenLoader(LoaderBase):
    language = "ja"

    def __init__(self, conn: sqlite3.Connection, *, batch_limit: int = 1000):
        self.conn = conn
        self.batch_limit = batch_limit
        self.vocab_sql = "INSERT INTO vocabulary (word) VALUES (?)"
        self.reading_sql = "INSERT INTO readings (vocab_id, reading, frequency_rank) VALUES (?, ?, ?)"

    @clock
    def load(self, entries: Iterable[WordReading]) -> None:
        ids = {}
        batch = []
        for entry in entries:
            if entry.word not in ids:
                cur = self.conn.execute(self.vocab_sql, (entry.word,))
                ids[entry.word] = cur.lastrowid
            batch.append((ids[entry.word], entry.reading, entry.frequency_rank))
            if len(batch) >= self.batch_limit:
                self.conn.executemany(self.reading_sql, batch)
                batch = []

        if len(batch) > 0:
            self.conn.executemany(self.reading_sql, batch)
        self.conn.commit()
