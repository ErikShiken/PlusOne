from typing import Iterator

def read_sentences(file_path: str) -> Iterator[str]:
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            current_line = line.strip()
            if not current_line:
                continue
            yield current_line