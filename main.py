import logging

from typing import Iterator, Iterable, Counter

from contextlib import contextmanager
from ETL.extractors.wanikani_extractor import WanikaniExtractor
from ETL.loaders.jiten_loader import JitenLoader
from ETL.models import Sentence, WordUnderstanding
from ETL.transform.jiten_transformer import JitenTransformer
from ETL.transform.wanikani_transformer import WanikaniTransformer
from classifier import DifficultyClassifier
from visitors.japanese.japanese_visitor import JapaneseVisitor
import os
import re
import sqlite3
from sudachipy import Dictionary
from ETL.extractors.jiten_extractor import JitenExtractor

from itertools import islice

logging.basicConfig(level=logging.DEBUG)

@contextmanager
def open_db(name):
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
    row = conn.execute(
        "SELECT id FROM vocabulary WHERE word = ?", (word,)
    ).fetchone()
    return row[0] if row else None

def load_known_words(conn: sqlite3.Connection, words: Iterable[str]) -> None:
    for word in words:
        vocab_id = find_vocab_id(conn, word)
        if vocab_id is None:
            continue
        conn.execute(
            "INSERT OR IGNORE INTO known_words (vocab_id) VALUES (?)", (vocab_id,)
        )

def update_times(conn: sqlite3.Connection, endpoint: str, last_synced: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO update_times (endpoint, last_synced) VALUES (?, ?)", (endpoint, last_synced)
    )

def is_katakana_only(word: str) -> bool:
    punctuation_class = "[、。「」『』！？・]"
    if re.search(rf"{punctuation_class}+", word):
        return False
    elif not word:
        return False

    return bool(re.fullmatch(r"[\u30a0-\u30ff]+", word))

def get_known_strings(words: Iterable[WordUnderstanding]) -> Iterator[str]:
    return (w.word for w in words if w.known)

def query_known_words() -> set[str]:
    with open_db("plusone.db") as conn:
        rows = conn.execute("""
                    SELECT vocabulary.word
                    FROM known_words
                    JOIN vocabulary ON vocabulary.id = known_words.vocab_id
                """).fetchall()
    return {row[0] for row in rows}

def get_srs_mapping() -> dict[str, str]:
    with open_db("plusone.db") as conn:
        rows = conn.execute("""
            SELECT characters, srs_state
            FROM wk_subjects_cache
            JOIN wk_assignments_cache ON wk_subjects_cache.subject_id = wk_assignments_cache.subject_id
        """).fetchall()
    return {row[0]: row[1] for row in rows}


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

        jiten_extractor = JitenExtractor("frequency_list_global.csv")
        rows = jiten_extractor.extract()
        entries = (JitenTransformer().transform(row) for row in rows)
        JitenLoader(conn).load(islice(entries, None))

        print("readings", conn.execute("SELECT COUNT(*) FROM readings").fetchone())
        print("vocabulary", conn.execute("SELECT COUNT(*) FROM vocabulary").fetchone())

    print("Chatper 14: mixins")
    print(JitenLoader.__mro__)

    print("chapter 16: operators")
    s = Sentence(["本", "を", "読んだ"])
    print(["昨日"] + s)  # Sentence(['昨日', '本', 'を', '読んだ'])

    print("chapter 17: iterators and generators")
    from ETL.extractors.sentence_reader import read_sentences
    iterator = islice(read_sentences("sentences_test.txt"), 3)
    for sentence in iterator:
        print(sentence)

    print("sorting sentences in ascending order based on n+x difficulty")
    with open_db("plusone.db") as conn:
        for sentence in conn.execute("SELECT * FROM classified_sentences ORDER BY unknown_count"):
            print(sentence)

    print("sorting sentences in no order based on n+x difficulty")
    with open_db("plusone.db") as conn:
        for row in conn.execute("SELECT * FROM classified_sentences"):
            print(row)

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

    my_words = query_known_words()
    japanese_understanding = JapaneseVisitor(my_words)
    JapaneseVisitor.set_grammar("global_rules.json")
    tokenizer = Dictionary().tokenizer()
    j2e_parts_of_speech = {'助詞': 'particle', '助動詞': 'auxiliary'}
    for sentence in read_sentences("sentences_test.txt"):
        morphemes = tokenizer.tokenize(sentence.__str__())

        print("Classify!")
        unknown_words = []
        for word in morphemes:
            match word.part_of_speech():
                case (('助詞' | '助動詞') as part_of_speech, *_):
                    print(j2e_parts_of_speech[part_of_speech], word.surface())

            unknown_words.append(word.dictionary_form())
        unknowns = japanese_understanding.get_unknowns(unknown_words)
        print(f"unknowns = {unknowns}")
        print(f"n+{DifficultyClassifier.classify(unknowns)}")