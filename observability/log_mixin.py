import logging

class LogMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

    def log(self, message: str, level: int = logging.INFO) -> None:
        self.logger.log(level, message)

    def warn(self, message: str):
        self.log(message, logging.WARNING)