"""Utility for reading sentence files line by line."""

from typing import Iterator

def read_sentences(file_path: str) -> Iterator[str]:
    """Yield non-empty lines from a UTF-8 encoded file."""
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            current_line = line.strip()
            if not current_line:
                continue
            yield current_line