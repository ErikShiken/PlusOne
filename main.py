from ETL.loaders.jiten_loader import JitenLoader
from ETL.transform.jiten_transformer import JitenTransformer
from visitors.japanese.japanese_sentence import JapaneseSentence
import sqlite3
from ETL.extractors.jiten_extractor import JitenExtractor

from itertools import islice

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    conn = sqlite3.connect("plusone.db")
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

    rows = JitenExtractor().extract("frequency_list_global.csv")
    entries = (JitenTransformer().transform(row) for row in rows)
    JitenLoader(conn).load(islice(entries, 2500))

    print(conn.execute("SELECT COUNT(*) FROM vocabulary").fetchone())

    user_known = JapaneseSentence.read_user_known()
    JapaneseSentence.set_grammar("global_rules.json")
    sentence = JapaneseSentence(user_known)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
