import logging
from pathlib import Path

_logger = logging.getLogger(__name__)


class Kontor:
    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"{__class__.__qualname__}({self.__dict__})"

    def link(self, file: Path) -> None:
        _logger.info(f"linking {file!r} into kontor...")

    def sync(self) -> None:
        _logger.info("synchronizing kontor...")
