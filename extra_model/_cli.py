import logging
import sys
from pathlib import Path

import click

from extra_model._errors import ExtraModelError
from extra_model._run import run
from extra_model._setup import setup

logger = logging.getLogger(__name__)


OUTPUT_PATH = "/io"
OUTPUT_FILENAME = "result.csv"
EMBEDDINGS_PATH = "/embeddings"


@click.command()
@click.argument("input_path", type=Path)
@click.option("-op", "--output-path", type=Path, default=OUTPUT_PATH, show_default=True)
@click.option(
    "-of", "--output-filename", type=Path, default=OUTPUT_FILENAME, show_default=True
)
@click.option(
    "-ep", "--embeddings-path", type=Path, default=EMBEDDINGS_PATH, show_default=True
)
@click.option("--debug", is_flag=True, help="Enable debug logging")
def entrypoint(
    input_path: Path,
    output_path: Path,
    output_filename: Path,
    embeddings_path: Path,
    debug: bool = False,
) -> None:
    """Run the Extra algorithm for unsupervised topic extraction.

    INPUT_PATH (required) is the path to the input csv file with the user generated texts. It must contain
    `CommentId` and `Comments` columns that are spelled exactly this way.

    OUTPUT_PATH (option) is the path to the output directory. Default is `/io`.

    OUTPUT_FILENAME (option) is the filename of the output file. Default is `result.csv`.
    The `.csv` file extension is not enforced. Please take care of this accordingly.

    EMBEDDINGS_PATH (option) is the path where the extra model will load the embeddings from.
    defaults to `/embeddings`.
    """
    logging.getLogger("extra_model").setLevel("DEBUG" if debug else "INFO")

    try:
        run(input_path, output_path, output_filename, embeddings_path)
        sys.exit(0)

    except ExtraModelError as e:
        logger.exception(e) if debug else logger.error(e)
        sys.exit(1)


@click.command()
@click.argument("output_path", type=Path, default=EMBEDDINGS_PATH)
def entrypoint_setup(output_path: Path) -> None:
    """Download resources.

    Will download and format glove embeddings.

    OUTPUT_PATH is the path to the output directory. Default is `/embeddings`.
    """
    try:
        setup(output_path)
        sys.exit(0)

    except ExtraModelError as e:
        logger.error(e)
        sys.exit(1)
