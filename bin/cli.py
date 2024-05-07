#! /usr/bin/env python
import logging

import click
from dotenv import load_dotenv

from cosmic_python.constants import LOG_LEVEL
from cosmic_python.utils import hello

# see `.env` for requisite environment variables
load_dotenv()


logging.basicConfig(
    level=logging.getLevelName(LOG_LEVEL),
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
)


@click.group()
@click.version_option(package_name="cosmic_python")
def cli():
    pass


@cli.command()
def main() -> None:
    """cosmic_python Main entrypoint"""
    click.secho(hello(), fg="green")


if __name__ == "__main__":
    cli()
