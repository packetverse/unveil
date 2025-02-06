from datetime import datetime
from logging.handlers import RotatingFileHandler

import os
import logging


class Logger(logging.Logger):
    def __init__(self, log_dir: str) -> None:
        self.log_dir = log_dir or os.path.expanduser("~/.unveil")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = f"unveil_{timestamp}.log"

        os.makedirs(self.log_dir, exist_ok=True)
        self.log_path = os.path.join(self.log_dir, self.log_file)
        log_level = logging.DEBUG

        self.logger = logging.getLogger("unveil")
        self.logger.setLevel(log_level)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler = RotatingFileHandler(self.log_path, maxBytes=1e6, backupCount=5)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)

    def exception(self, message: str) -> None:
        self.logger.exception(message)
