from typing import Callable

HANDLERS: dict[str, Callable] = {}

def handles(kind: str):
    def register(func):
        if kind in HANDLERS:
            raise ValueError(
                f"{kind!r} already handled by {HANDLERS[kind].__name__}"
            )
        HANDLERS[kind] = func
        return func
    return register