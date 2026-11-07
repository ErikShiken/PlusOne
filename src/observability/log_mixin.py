"""Mixin that provides a class-named logger and convenience logging methods."""

import logging


class LogMixin:
    """Mixin that gives subclasses a logger named after their class."""

    def __init__(self, *args, **kwargs):
        """Initialize the logger after cooperative superclass init."""
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

    def log(self, message: str, level: int = logging.INFO) -> None:
        """Log a message at the given level."""
        self.logger.log(level, message)

    def warn(self, message: str):
        """Log a message at WARNING level."""
        self.log(message, logging.WARNING)
