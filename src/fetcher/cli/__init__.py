import logging

import click

from fetcher.__about__ import __version__


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__)
def fetcher() -> None:
    logging.basicConfig(level=logging.INFO)
    click.echo("Hello world!")
