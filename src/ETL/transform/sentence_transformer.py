"""Transformer that scores Japanese sentences by counting unknown words."""

from sudachipy import Dictionary

from src.ETL.transform.transform_base import TransformBase
from src.classifier import DifficultyClassifier
from src.visitors.japanese.japanese_visitor import JapaneseVisitor
from src.visitors.sentence_visitor import SentenceVisitor


class SentenceTransformer(TransformBase[str, tuple[str, int]]):
    """Tokenizes a sentence and returns it with a difficulty score."""

    def __init__(self, tokenizer, understanding: SentenceVisitor):
        """Initialize with a Sudachi tokenizer and a sentence visitor."""
        self.tokenizer = tokenizer
        self.visitor = understanding

    def transform(self, sentence_under_review: str) -> tuple[str, int]:
        """Return the sentence paired with its difficulty classification."""
        morphemes = self.tokenizer.tokenize(sentence_under_review)

        unknown_words = []
        for word in morphemes:
            match word.part_of_speech():
                case (('助詞' | '助動詞') as part_of_speech, *_):
                    pass  # print(j2e_parts_of_speech[part_of_speech], word.surface())

            unknown_words.append(word.dictionary_form())
        return sentence_under_review, DifficultyClassifier.classify(self.visitor.get_unknowns(unknown_words))

def build_transformer(known_words: set[str]) -> SentenceTransformer:
    """Construct a SentenceTransformer wired with grammar and a Sudachi tokenizer."""
    understanding = JapaneseVisitor(known_words)
    JapaneseVisitor.set_grammar("global_rules.json")
    tokenizer = Dictionary().tokenizer()
    return SentenceTransformer(tokenizer, understanding)

def transform_worker(known_words, jobs, results) -> None:
    """Consume sentence batches from jobs, transform them, and push results."""
    transformer = build_transformer(known_words)
    while (batch := jobs.get()) is not None:
        batch_results = []
        for sentence in batch:
            batch_results.append(transformer.transform(sentence))
        results.put(batch_results)
    results.put(None)
