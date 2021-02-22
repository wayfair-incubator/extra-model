import logging
import sys
from pathlib import Path

import click

from extra_model._errors import ExtraModelError
from extra_model._run import run

logger = logging.getLogger(__name__)


@click.command()
@click.argument("input_path", type=Path)
@click.argument("output_path", type=Path, default="/app/output")
@click.option("--debug", is_flag=True)
def entrypoint(input_path: Path, output_path: Path, debug: bool = False) -> None:
    """Parse and handle CLI arguments.

    :param input_path: Path to the file that should be used for running extra_model on.
    :param output_path: Path to the file that output of extra_model is going to be saved.
    :param debug: If set to True, sets log level for the application to DEBUG, else WARNING.
    :return: Dictionary with input_path and output_path set to specified values
    """
    logging.getLogger("extra_model").setLevel("DEBUG" if debug else "INFO")

    try:
        run(input_path, output_path)
    except ExtraModelError as e:
        logger.exception(e) if debug else logger.error(e)
        sys.exit(1)
