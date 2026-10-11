import logging
from typing import Iterable

from ETL.loaders.jiten_loader import JitenLoader
from ETL.transform.jiten_transformer import JitenTransformer
from visitors.japanese.japanese_sentence import JapaneseSentence
from visitors.rules.unknown_rule import unknown_rule
import sqlite3
from ETL.extractors.jiten_extractor import JitenExtractor

from itertools import islice

logging.basicConfig(level=logging.DEBUG)

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
    conn.commit()

if __name__ == '__main__':
    conn = sqlite3.connect("plusone.db")
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary (
                id              INTEGER PRIMARY KEY,
                word            TEXT NOT NULL,
                synonym_id      INTEGER REFERENCES vocabulary(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id        INTEGER PRIMARY KEY,
                vocab_id  INTEGER NOT NULL REFERENCES vocabulary(id),
                reading   TEXT NOT NULL,
                frequency_rank  INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS known_words (
                id        INTEGER PRIMARY KEY,
                vocab_id  INTEGER NOT NULL UNIQUE REFERENCES vocabulary(id)
            )
        """)

        rows = JitenExtractor().extract("frequency_list_global.csv")
        entries = (JitenTransformer().transform(row) for row in rows)
        JitenLoader(conn).load(islice(entries, 2500))
        load_known_words(conn, JapaneseSentence.read_user_known("user_known.dat"))

        print("readings", conn.execute("SELECT COUNT(*) FROM readings").fetchone())
        print("vocabulary", conn.execute("SELECT COUNT(*) FROM vocabulary").fetchone())
    finally:
        conn.close()

    sentence = JapaneseSentence.from_file("user_known.dat", unknown_rule)
    sentence.set_grammar("global_rules.json")

    sentence.visit("vocabulary", "食べる")
