from ETL.transform.transform_base import TransformBase
from visitors.sentence_visitor import SentenceVisitor

class SentenceTransformer(TransformBase[str, tuple[str, int]]):
    def __init__(self, tokenizer, understanding: SentenceVisitor):
        self.tokenizer = tokenizer
        self.visitor = understanding

    def transform(self, sentence: str):
        morphemes = self.tokenizer.tokenize(sentence)

        unknown_words = []
        for word in morphemes:
            match word.part_of_speech():
                case (('助詞' | '助動詞') as part_of_speech, *_):
                    pass  # print(j2e_parts_of_speech[part_of_speech], word.surface())

            unknown_words.append(word.dictionary_form())
        return sentence, self.visitor.get_unknowns(unknown_words)