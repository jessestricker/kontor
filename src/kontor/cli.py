import logging
from pathlib import Path

import click

from . import Kontor

_logger = logging.getLogger(__name__)


@click.group(help="Manages your home directory.")
@click.option("--debug/--no-debug", help="Print information useful for debugging.")
@click.pass_context
def main(ctx: click.Context, *, debug: bool) -> None:
    # setup logging
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # create kontor object
    kontor = Kontor()
    _logger.debug("kontor=%r", kontor)

    ctx.obj = kontor


@main.command(help="Adds a file to the kontor.")
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_obj
def link(kontor: Kontor, file: Path) -> None:
    kontor.link(file)


# called 'list_command' to not shadow builtin 'list'
@main.command(help="List all files in the kontor.")
@click.pass_obj
def list_command(kontor: Kontor) -> None:
    kontor.list()


@main.command(help="Synchronizes the home directory with the kontor.")
@click.pass_obj
def sync(kontor: Kontor) -> None:
    kontor.sync()
