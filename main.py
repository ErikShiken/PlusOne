import logging
import re
from typing import Iterator, Iterable, Sequence, Counter

import json

from ETL.extractors.wanikani_extractor import WanikaniExtractor
from ETL.loaders.jiten_loader import JitenLoader
from ETL.models import Sentence, WordUnderstanding
from ETL.transform.jiten_transformer import JitenTransformer
from ETL.transform.wanikani_transformer import WanikaniTransformer
from classifier import DifficultyClassifier
from visitors.japanese.japanese_visitor import JapaneseVisitor
import os
import requests
import sqlite3
from ETL.extractors.jiten_extractor import JitenExtractor

from itertools import islice

logging.basicConfig(level=logging.DEBUG)

PUNCTUATION = re.compile(r"[、。「」『』！？・]+")

def is_punctuation(token: str) -> bool:
    return bool(PUNCTUATION.fullmatch(token))

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

def is_katakana_only(word: str) -> bool:
    punctuation_class = "[、。「」『』！？・]"
    if re.search(rf"{punctuation_class}+", word):
        return False
    elif not word:
        return False

    return bool(re.fullmatch(r"[\u30a0-\u30ff]+", word))

def get_known_strings(words: Iterable[WordUnderstanding]) -> Iterator[str]:
    return (w.word for w in words if w.known)

if __name__ == '__main__':
    conn = sqlite3.connect("plusone.db")
    try:
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

        jiten_extractor = JitenExtractor("frequency_list_global.csv")
        rows = jiten_extractor.extract()
        entries = (JitenTransformer().transform(row) for row in rows)
        JitenLoader(conn).load(islice(entries, None))

        print("readings", conn.execute("SELECT COUNT(*) FROM readings").fetchone())
        print("vocabulary", conn.execute("SELECT COUNT(*) FROM vocabulary").fetchone())
    finally:
        conn.close()

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

    print("sudachipy example")
    import sys

    print(sys.executable)
    from sudachipy import Dictionary, SplitMode

    tokenizer = Dictionary().tokenizer()

    morphemes = tokenizer.tokenize("国会議事堂前駅")
    print(morphemes[0].surface())  # '国会議事堂前駅'
    print(morphemes[0].reading_form())  # 'コッカイギジドウマエエキ'
    print(morphemes[0].part_of_speech())  # ['名詞', '固有名詞', '一般', '*', '*', '*']

    morphemes = tokenizer.tokenize("国会議事堂前駅", SplitMode.A)
    my_first_sentence = [m.surface() for m in morphemes]
    print(my_first_sentence)  # ['国会', '議事', '堂', '前', '駅']

    morphemes = tokenizer.tokenize("国会議事堂前駅", SplitMode.C)
    my_first_sentence = [m.surface() for m in morphemes]
    print(my_first_sentence)

    morphemes = tokenizer.tokenize("私は日本語を勉強した。")
    simple_sentence = [m.surface() for m in morphemes]
    print(simple_sentence)

    morphemes = tokenizer.tokenize("私は日本語を勉強した。")
    dictionary_form = [m.dictionary_form() for m in morphemes]
    print(dictionary_form)

    print("sorting sentences in ascending order based on n+x difficulty")
    try:
        conn = sqlite3.connect("plusone.db")
        for sentence in conn.execute("SELECT * FROM classified_sentences ORDER BY unknown_count"):
            print(sentence)
    finally:
        conn.close()

    print("sorting sentences in no order based on n+x difficulty")
    try:
        conn = sqlite3.connect("plusone.db")
        for row in conn.execute("SELECT * FROM classified_sentences"):
            print(row)
    finally:
        conn.close()

    wani_extractor = WanikaniExtractor()
    mapping = wani_extractor.extract()
    counts = Counter(mapping.values())
    print("counts = ", counts)
    print("Enlightened = ", counts[8])
    print("Burned = ", counts[9])
    print(len(mapping))

    transform = WanikaniTransformer()
    actual_words = transform.transform(mapping)
    print("known words = ", sum(1 for word in actual_words if word.known))
    print("difference = ", len(mapping) - len(actual_words))

    try:
        conn = sqlite3.connect("plusone.db")
        load_known_words(conn, get_known_strings(actual_words))
        count_in_db = conn.execute("SELECT COUNT(*) FROM known_words").fetchone()
        print("number of known words in DB = ", count_in_db)
        print("difference is ", len(actual_words) - count_in_db[0])
    finally:
        conn.close()

    all_squiggle = sum(1 for word in mapping if "\u301c" in word)
    known_squiggle = sum(1 for word, stage in mapping.items()
                         if "\u301c" in word and stage >= 8)

    print("all 〜 words = ", all_squiggle)  # expect 65
    print("known 〜 words = ", known_squiggle)  # expect 63