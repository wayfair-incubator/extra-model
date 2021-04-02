import logging
import subprocess  # nosec
from pathlib import Path
from typing import List

from gensim.models import KeyedVectors
from gensim.test.utils import datapath

from extra_model._errors import ExtraModelError

URL = "http://downloads.cs.stanford.edu/nlp/data/glove.840B.300d.zip"

logger = logging.getLogger(__name__)


def setup(output_path: Path) -> None:
    """Docstring."""
    logging.basicConfig(level="INFO", format="  %(message)s")

    logger.info("")
    logger.info("extra-model-setup will perform the following actions:")
    logger.info("  1. Download embeddings")
    logger.info("  2. Unzip embeddings")
    logger.info("  3. Format embeddings")
    logger.info("This process will take approximately 40 minutes.")
    logger.info("Setup can be safely re-run if exited prematurely.")
    logger.info("")

    if input("  Would you like to continue? [y/n]: ").lower() != "y":
        return

    files_to_cleanup: List[Path] = []

    file_zipped = download_file(URL, output_path)
    files_to_cleanup.append(file_zipped)

    file_unzipped = unzip_file(file_zipped, output_path)
    files_to_cleanup.append(file_unzipped)

    format_file(file_unzipped, output_path)
    cleanup(files_to_cleanup)

    logger.info("Done!")


def download_file(url: str, output_path: Path) -> Path:
    """Download embeddings file."""
    filename = url.split("/")[-1]
    output_file = output_path / filename

    if not output_file.is_file():
        logger.info("Downloading embeddings file.")
        logger.info("This will take approximately 20 minutes.")
        run_subprocess(["curl", url, "-o", str(output_file)])

    else:
        logger.info(f"Embeddings file {output_file} detected, downloading skipped!")

    return output_file


def unzip_file(file: Path, output_path: Path) -> Path:
    """Unzip embeddings file."""
    output_file = output_path / f"{file.stem}.txt"

    if not output_file.is_file():
        logger.info("Unzipping file. This will take approximately 5 minutes.")
        run_subprocess(["unzip", str(file), "-d", str(output_path)])

    else:
        logger.info(f"File {output_file} detected, unzipping skipped!")

    return output_file


def format_file(file: Path, output_path: Path) -> None:
    """Format embeddings file."""
    output_file = output_path / f"{file.stem}"
    if not output_file.is_file():
        logger.info("Formatting file. This will take approximately 10 minutes.")
        glove_file = datapath(str(file))
        model = KeyedVectors.load_word2vec_format(
            glove_file, binary=False, no_header=True
        )
        model.save(str(output_file))

    else:
        logger.info(f"File {output_file} detected, formatting skipped!")


def cleanup(files: List[Path]) -> None:
    """Cleanup setup cruft."""
    logger.info("Cleaning up setup cruft...")

    for file in files:
        logger.info(f"Deleting {file}...")
        file.unlink()


def run_subprocess(command: List[str]) -> None:
    """Run subprocess."""
    try:
        subprocess.run(" ".join(command), check=True, shell=True)  # nosec

    except subprocess.CalledProcessError as e:
        raise ExtraModelError(f"Subprocess error: {e.stderr}")
