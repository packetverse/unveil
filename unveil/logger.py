from rich.logging import RichHandler
from unveil import config

import logging


class Logger:
    def __init__(self) -> None:
        self.logger = logging.getLogger("rich")
        self.logger.setLevel(logging.DEBUG)

        self.file_handler = logging.FileHandler("unveil.log")
        self.file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(self.file_handler)

        self.rich_handler = None
        self.update_stream_handler()

    def update_stream_handler(self) -> None:
        if config.verbose:
            if not self.rich_handler:
                self.rich_handler = RichHandler()
                self.rich_handler.setFormatter(
                    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                )
                self.logger.addHandler(self.rich_handler)
        else:
            if self.rich_handler:
                self.logger.removeHandler(self.rich_handler)
                self.rich_handler = None

    def info(self, message) -> None:
        self.update_stream_handler()
        self.logger.info(message)

    def error(self, message) -> None:
        self.update_stream_handler()
        self.logger.error(message)
