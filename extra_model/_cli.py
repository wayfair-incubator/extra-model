import logging
import sys
from pathlib import Path

import click

from extra_model._errors import ExtraModelError
from extra_model._run import run

logger = logging.getLogger(__name__)


DEFAULT_OUTPUT_PATH = "/io"


@click.command()
@click.argument("input_path", type=Path)
@click.argument("output_path", type=Path, default=DEFAULT_OUTPUT_PATH)
@click.option("--debug", is_flag=True, help="Enable debug logging")
def entrypoint(input_path: Path, output_path: Path, debug: bool = False) -> None:
    """Run the Extra algorithm for unsupervised topic extraction.

    INPUT_PATH is the path to the input parquet file with the user generated texts.
    
    OUTPUT_PATH is the path to the output directory. Default is `/io`
    """
    logging.getLogger("extra_model").setLevel("DEBUG" if debug else "INFO")

    try:
        run(input_path, output_path)
    except ExtraModelError as e:
        logger.exception(e) if debug else logger.error(e)
        sys.exit(1)
