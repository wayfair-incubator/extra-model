import logging
from pathlib import Path
from typing import Dict

import click

LOGGER = logging.getLogger(__name__)


@click.command()
@click.argument("input_path", type=Path)
@click.argument("output_path", type=Path, default="/app/output")
@click.option("--debug", is_flag=True)
def entrypoint(
    input_path: Path, output_path: Path, debug: bool = False
) -> Dict[str, Path]:

    """
    Parse and handle CLI arguments.

    :param input_path: Path to the file that should be used for running extra_model on.
    :param output_path: Path to the file that output of extra_model is going to be saved.
    :param debug: If set to True, sets log level for the application to DEBUG, else WARNING.
    :return: Dictionary with input_path and output_path set to specified values
    """
    logging.getLogger("extra_model").setLevel("DEBUG" if debug else "WARNING")

    return {"input_path": input_path, "output_path": output_path}
