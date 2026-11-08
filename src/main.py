"""Main entry point for the PlusOne application.

This module orchestrates the ETL pipeline: it loads vocabulary data from Jiten,
syncs Wanikani SRS data, and classifies Tatoeba sentences by difficulty.
"""

import logging
import psutil

from typing import Iterator, Iterable

from contextlib import contextmanager

from src.ETL.extractors.tatoeba_extractor import TatoebaExtractor
from src.ETL.extractors.wanikani_extractor import WanikaniExtractor
from src.ETL.loaders.jiten_loader import JitenLoader
from src.ETL.models import WordUnderstanding
from src.ETL.transform.jiten_transformer import JitenTransformer
from src.ETL.transform.sentence_transformer import transform_worker
from src.ETL.transform.wanikani_transformer import WanikaniTransformer
from multiprocessing import Process, Queue
import re
import sqlite3
import time
from src.ETL.extractors.jiten_extractor import JitenExtractor

from itertools import islice, batched

logging.basicConfig(level=logging.DEBUG)

@contextmanager
def open_db(name):
    """Open a SQLite database connection with automatic commit/rollback."""
    connection = sqlite3.connect(name)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def find_vocab_id(conn: sqlite3.Connection, word: str) -> int | None:
    """Look up the vocabulary ID for a given word."""
    row = conn.execute(
        "SELECT id FROM vocabulary WHERE word = ?", (word,)
    ).fetchone()
    return row[0] if row else None

def load_known_words(conn: sqlite3.Connection, words: Iterable[str]) -> None:
    """Insert known words into the known_words table."""
    for word in words:
        vocab_id = find_vocab_id(conn, word)
        if vocab_id is None:
            continue
        conn.execute(
            "INSERT OR IGNORE INTO known_words (vocab_id) VALUES (?)", (vocab_id,)
        )

def update_times(conn: sqlite3.Connection, endpoint: str, last_synced: str) -> None:
    """Record the last sync time for an API endpoint."""
    conn.execute(
        "INSERT OR REPLACE INTO update_times (endpoint, last_synced) VALUES (?, ?)",
        (endpoint, last_synced)
    )

def is_katakana_only(word: str) -> bool:
    """Return True if the word consists solely of katakana characters."""
    punctuation_class = "[、。「」『』！？・]"
    if re.search(rf"{punctuation_class}+", word):
        return False
    elif not word:
        return False

    return bool(re.fullmatch(r"[\u30a0-\u30ff]+", word))

def get_known_strings(words: Iterable[WordUnderstanding]) -> Iterator[str]:
    """Yield the word strings from WordUnderstanding objects marked as known."""
    return (w.word for w in words if w.known)

def query_known_words() -> set[str]:
    """Query the database for all known words."""
    with open_db("plusone.db") as conn:
        rows = conn.execute("""
                    SELECT vocabulary.word
                    FROM known_words
                    JOIN vocabulary ON vocabulary.id = known_words.vocab_id
                """).fetchall()
    return {row[0] for row in rows}

def get_srs_mapping() -> dict[str, str]:
    """Query the database for Wanikani SRS state mappings."""
    with open_db("plusone.db") as conn:
        rows = conn.execute("""
            SELECT characters, srs_state
            FROM wk_subjects_cache
            JOIN wk_assignments_cache ON wk_subjects_cache.subject_id = wk_assignments_cache.subject_id
        """).fetchall()
    return {row[0]: row[1] for row in rows}

def start_jobs(procs: int, transform_jobs, transform_results, known_words: set[str],
               sentences: Iterable[str]) -> None:
    """Start worker processes to transform sentences in parallel."""
    batch_size = 100
    for batch in batched(sentences, batch_size):
        transform_jobs.put(batch)

    for _ in range(procs):
        proc = Process(target=transform_worker, args=(known_words, transform_jobs,
                                                      transform_results))
        proc.start()
        transform_jobs.put(None)

def report(num_procs: int, process_results) -> list[tuple[str, int]]:
    """Collect transformation results from all worker processes."""
    classifications_to_report = []
    procs_done = 0
    while procs_done < num_procs:
        result = process_results.get()
        if result is None:
            procs_done += 1
        else:
            classifications_to_report.extend(result)
    return classifications_to_report

def save_classified(db_conn, classified: list[tuple[str, int]]) -> None:
    """Save classified sentences to the database."""
    db_conn.executemany(
        "INSERT OR REPLACE INTO classified_sentences (sentence, unknown_count) VALUES (?, ?)",
        classified,
    )

if __name__ == '__main__':
    with open_db("plusone.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary (
                id              INTEGER PRIMARY KEY,
                word            TEXT NOT NULL UNIQUE,
                synonym_id      INTEGER REFERENCES vocabulary(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id        INTEGER PRIMARY KEY,
                vocab_id  INTEGER NOT NULL REFERENCES vocabulary(id),
                reading   TEXT NOT NULL,
                frequency_rank  INTEGER,
                UNIQUE(vocab_id, reading)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS known_words (
                id        INTEGER PRIMARY KEY,
                vocab_id  INTEGER NOT NULL UNIQUE REFERENCES vocabulary(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS classified_sentences (
                id        INTEGER PRIMARY KEY,
                sentence  TEXT NOT NULL UNIQUE,
                unknown_count     INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wk_subjects_cache (
                subject_id        INTEGER PRIMARY KEY,
                characters  TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wk_assignments_cache (
                subject_id        INTEGER PRIMARY KEY,
                srs_state  INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS update_times (
                endpoint        TEXT PRIMARY KEY,
                last_synced  TEXT NOT NULL
            )
        """)

        jiten_extractor = JitenExtractor("../frequency_list_global.csv")
        rows = jiten_extractor.extract()
        entries = (JitenTransformer().transform(row) for row in rows)
        JitenLoader(conn).load(islice(entries, None))

        print("readings", conn.execute("SELECT COUNT(*) FROM readings").fetchone())
        print("vocabulary", conn.execute("SELECT COUNT(*) FROM vocabulary").fetchone())

    with open_db("plusone.db") as conn:
        subject_update_time = conn.execute("SELECT last_synced FROM update_times WHERE endpoint = 'subjects'").fetchone()
        if subject_update_time:
            subject_update_time = subject_update_time[0]
        print("subject update time ", subject_update_time)
        assignment_update_time = conn.execute(
            "SELECT last_synced FROM update_times WHERE endpoint = 'assignments'").fetchone()
        if assignment_update_time:
            assignment_update_time = assignment_update_time[0]
        print("assignment update time ", assignment_update_time)

    wani_extractor = WanikaniExtractor(last_subject_update_time=subject_update_time, last_assignment_update_time=assignment_update_time)
    subjects, subject_update_time = wani_extractor.extract_subjects()
    print("subject update time ", subject_update_time)
    if subject_update_time:
        with open_db("plusone.db") as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO wk_subjects_cache (subject_id, characters) VALUES (?, ?)",
                subjects.items(),
            )
            update_times(conn, "subjects", subject_update_time)
            print(conn.execute("SELECT COUNT(*) FROM wk_subjects_cache").fetchone())

    assignments, assignments_update_time = wani_extractor.extract_assignments()
    print("assignments update time ", assignments_update_time)

    if assignments_update_time:
        with open_db("plusone.db") as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO wk_assignments_cache (subject_id, srs_state) VALUES (?, ?)",
                assignments.items(),
            )
            update_times(conn, "assignments", assignments_update_time)
            print(conn.execute("SELECT COUNT(*) FROM wk_assignments_cache").fetchone())

    with open_db("plusone.db") as conn:
        print(conn.execute("SELECT * FROM update_times").fetchall())

    mapping = get_srs_mapping()
    transform = WanikaniTransformer()
    actual_words = transform.transform(mapping)

    with open_db("plusone.db") as conn:
        load_known_words(conn, get_known_strings(actual_words))
        count_in_db = conn.execute("SELECT COUNT(*) FROM known_words").fetchone()
        print("number of known words in DB = ", count_in_db)
        print("difference is ", len(actual_words) - count_in_db[0])

    print("start tatoeba extractor!")
    start = time.monotonic()
    with TatoebaExtractor() as ex:
        jobs = Queue()
        results = Queue()
        allowed_procs = psutil.cpu_count(logical=False)
        start_jobs(allowed_procs, jobs, results, query_known_words(), ex.extract())
        classified = report(allowed_procs, results)

    total = time.monotonic() - start
    with open_db("plusone.db") as db_conn:
        save_classified(db_conn, classified)
    print("time taken = ", total, "seconds")