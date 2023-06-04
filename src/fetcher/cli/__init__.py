import asyncio
import logging

import click

from fetcher import fetch
from fetcher.__about__ import __version__


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("url")
@click.option("-v", "--verbose", is_flag=True)
@click.version_option(version=__version__)
def fetcher(url: str, verbose: bool) -> None:  # noqa: FBT001
    _configure_logging()
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    response = asyncio.run(fetch(url))

    if not response.ok:
        msg = f"Server returned status '{response.status} {response.status_text}'"
        raise click.ClickException(msg)

    click.echo("Ok")


def _configure_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger = logging.getLogger("fetch")
    logger.addHandler(handler)
    logger.propagate = False
