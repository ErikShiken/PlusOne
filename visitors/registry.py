from typing import Callable

HANDLERS: dict[str, Callable] = {}

def handles(kind: str):
    def register(func):
        HANDLERS[kind] = func
        return func
    return register