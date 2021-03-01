import subprocess
import datetime
import logging
from typing import List
from pathlib import Path

from gensim.test.utils import datapath, get_tmpfile 
from gensim.models import KeyedVectors 
from gensim.scripts.glove2word2vec import glove2word2vec 

from extra_model._errors import ExtraModelError


URL = "http://downloads.cs.stanford.edu/nlp/data/glove.840B.300d.zip"
OUTPUT = Path("/models")

logger = logging.getLogger(__name__)


def setup(url: str = URL, output: Path = OUTPUT) -> None:

    logging.basicConfig(level="INFO", format="  %(message)s")
    
    logger.info("")
    logger.info("extra-model-setup will perform the following actions:")
    logger.info("  1. Download embeddings")
    logger.info("  2. Unzip embeddings")
    logger.info("  3. Format embeddings")
    logger.info("This process will take approximately 40 minutes.")
    logger.info("Setup can be safely re-run if exited prematurely.")
    logger.info("")
    
    if input("  Would you like to continue? [y/n]: ").lower() == "n":
        exit(0)
    
    files_to_cleanup: List[Path] = []
    
    file_zipped = download_file(url, output)
    files_to_cleanup.append(file_zipped)
    
    file_unzipped = unzip_file(file_zipped, output)
    files_to_cleanup.append(file_unzipped)
    
    format_file(file_unzipped, output)
    cleanup(files_to_cleanup)
    
    logger.info("Done!")


def download_file(url: str, output: Path) -> Path:
    """Download embeddings file."""
    
    filename = url.split("/")[-1]
    output_file = output / filename
    
    if not output_file.is_file():
        logger.info("Downloading embeddings file.")
        logger.info("This will take approximately 20 minutes.")
        run_subprocess(["curl", url, "-o", str(output_file)])
        
    else:
        logger.info(f"Embeddings file {output_file} detected, downloading skipped!")
        
    return output_file


def unzip_file(file: Path, output: Path) -> Path:
    """Unzip embeddings file."""
    
    output_file = output / f"{file.stem}.txt"
    
    if not output_file.is_file():
        logger.info("Unzipping file. This will take approximately 5 minutes.")
        run_subprocess(["unzip", str(file), "-d", str(output)])
        
    else:
        logger.info(f"File {output_file} detected, unzipping skipped!")
        
    return output_file


def format_file(file: Path, output: Path) -> None:
    """Format embeddings file."""
    
    output_file = output / f"{file.stem}"
    if not output_file.is_file():
        logger.info("Formatting file. This will take approximately 10 minutes.")
        glove_file = datapath(str(file))
        tmp_file = get_tmpfile("test_word2vec.txt") 
        _ = glove2word2vec(glove_file, tmp_file) 
        model = KeyedVectors.load_word2vec_format(tmp_file) 
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
