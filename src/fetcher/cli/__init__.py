import asyncio
import logging

import click

from fetcher import fetch
from fetcher.__about__ import __version__


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("url")
@click.version_option(version=__version__)
def fetcher(url: str) -> int:
    logging.basicConfig(level=logging.INFO)
    response = asyncio.run(fetch(url))

    if not response.ok:
        msg = f"Server returned status '{response.status} {response.status_text}'"
        raise click.ClickException(msg)

    click.echo("Ok")
