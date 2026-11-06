from ETL.transform.transform_base import TransformBase
from classifier import DifficultyClassifier
from visitors.japanese.japanese_visitor import JapaneseVisitor
from visitors.sentence_visitor import SentenceVisitor

from sudachipy import Dictionary

class SentenceTransformer(TransformBase[str, tuple[str, int]]):
    def __init__(self, tokenizer, understanding: SentenceVisitor):
        self.tokenizer = tokenizer
        self.visitor = understanding

    def transform(self, sentence: str) -> tuple[str, int]:
        morphemes = self.tokenizer.tokenize(sentence)

        unknown_words = []
        for word in morphemes:
            match word.part_of_speech():
                case (('助詞' | '助動詞') as part_of_speech, *_):
                    pass  # print(j2e_parts_of_speech[part_of_speech], word.surface())

            unknown_words.append(word.dictionary_form())
        return sentence, DifficultyClassifier.classify(self.visitor.get_unknowns(unknown_words))

def build_transformer(known_words: set[str]) -> SentenceTransformer:
    understanding = JapaneseVisitor(known_words)
    JapaneseVisitor.set_grammar("global_rules.json")
    tokenizer = Dictionary().tokenizer()
    return SentenceTransformer(tokenizer, understanding)