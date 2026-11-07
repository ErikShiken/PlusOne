"""Registry mapping token kinds to their visitor handler functions."""

from typing import Callable

HANDLERS: dict[str, Callable] = {}
"""Mapping of token kind names to the functions that handle them."""


def handles(kind: str):
    """Decorator that registers a function as the handler for a token kind."""
    def register(func):
        """Register func under kind, raising if kind is already registered."""
        if kind in HANDLERS:
            raise ValueError(
                f"{kind!r} already handled by {HANDLERS[kind].__name__}"
            )
        HANDLERS[kind] = func
        return func
    return register
