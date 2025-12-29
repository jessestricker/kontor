import argparse
import logging
from dataclasses import dataclass

_logger = logging.getLogger()


def main() -> None:
    _setup_logging()

    cli = _parse_cli()
    if cli.debug:
        _logger.setLevel(logging.DEBUG)
    _logger.debug("cli=%r", cli)

    _logger.info("Hello from kontor!")


def _setup_logging() -> None:
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.INFO,
    )


def _parse_cli() -> _Cli:
    parser = argparse.ArgumentParser(
        description="Manages your home directory.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="print information helpful for debugging",
    )

    args = parser.parse_args()
    return _Cli(**vars(args))


@dataclass
class _Cli:
    debug: bool
