import logging
from typing import Iterable, Sequence

import json

from ETL.extractors.wanikani_extractor import WanikaniExtractor
from ETL.loaders.jiten_loader import JitenLoader
from ETL.models import Sentence
from ETL.transform.jiten_transformer import JitenTransformer
from classifier import DifficultyClassifier
from visitors.japanese.japanese_visitor import JapaneseVisitor
import os
import requests
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS classified_sentences (
                id        INTEGER PRIMARY KEY,
                sentence  TEXT NOT NULL UNIQUE,
                label     TEXT NOT NULL
            )
        """)

        jiten_extractor = JitenExtractor("frequency_list_global.csv")
        rows = jiten_extractor.extract()
        entries = (JitenTransformer().transform(row) for row in rows)
        JitenLoader(conn).load(islice(entries, 2500))
        load_known_words(conn, JapaneseVisitor.read_user_known("user_known.dat"))

        print("readings", conn.execute("SELECT COUNT(*) FROM readings").fetchone())
        print("vocabulary", conn.execute("SELECT COUNT(*) FROM vocabulary").fetchone())
    finally:
        conn.close()

    visitor = JapaneseVisitor.from_file("user_known.dat")
    visitor.set_grammar("global_rules.json")

    visitor.visit("vocabulary", "食べる")
    print("classify!")
    print(DifficultyClassifier.classify(visitor.unknowns))

    s = Sentence(["昨日", "買った", "本", "を", "読んだ"])
    print(s)
    print(len(s))
    print(s[1:3])
    print(s[-1])
    print("を" in s)

    a = Sentence(["本", "を", "読んだ"])
    b = Sentence(["本", "を", "読んだ"])
    print(a == b)  # True
    print(a == ["本"])

    a = Sentence(["本", "を", "読んだ"])
    b = Sentence(["本", "を", "読んだ"])
    c = Sentence(["猫", "が", "寝て", "いる"])

    print(hash(a) == hash(b))  # True: same words, same hash
    print(len({a, b, c}))  # 2: the set dropped the duplicate

    s = Sentence(["昨日", "買った", "本", "を", "読んだ"])
    print("Sequence examples: chapter 13")
    print(s.index("本"))  # 2
    print(s.count("を"))  # 1
    print(list(reversed(s)))  # ['読んだ', 'を', '本', '買った', '昨日']
    print(isinstance(s, Sequence))  # True

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

    new_visitor = JapaneseVisitor.from_file("user_known.dat")
    new_visitor.set_grammar("global_rules.json")

    for morpheme in morphemes:
        if 1548 > morpheme.part_of_speech_id() or morpheme.part_of_speech_id() > 1554:
            new_visitor.visit("vocabulary", morpheme.dictionary_form())

    print(new_visitor.user_known)
    print(DifficultyClassifier.classify(new_visitor.unknowns))

    print("iterate over the sentences_text and classify each one")
    iterator = read_sentences("sentences_test.txt")
    known_words = JapaneseVisitor.read_user_known("user_known.dat")
    conn = sqlite3.connect("plusone.db")
    try:
        for sentence in iterator:
            tokens = tokenizer.tokenize(sentence.__str__())
            sentences_visitor = JapaneseVisitor(known_words)
            for t in tokens:
                if 1548 > t.part_of_speech_id() or t.part_of_speech_id() > 1554:
                    sentences_visitor.visit("vocabulary", t.dictionary_form())

            label = DifficultyClassifier.classify(sentences_visitor.unknowns)
            print(label)
            conn.execute(
                "INSERT OR IGNORE INTO classified_sentences (sentence, label) VALUES (?, ?)",
                (str(sentence), str(label)),
            )
            conn.commit()
    finally:
        conn.close()

    try:
        conn = sqlite3.connect("plusone.db")
        for row in conn.execute("SELECT * FROM classified_sentences"):
            print(row)
    finally:
        conn.close()

    wani_extractor = WanikaniExtractor()
    mapping = wani_extractor.extract()
    print(mapping)
    print(len(mapping))