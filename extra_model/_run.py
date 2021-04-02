import logging
from pathlib import Path

import pandas as pd

from extra_model._models import ExtraModel

MODELS_FOLDER = Path("./embeddings")
OUTPUT_FILE = Path("result.csv")

logger = logging.getLogger(__name__)


def run(
    input_path: Path,
    output_path: Path,
    output_filename: Path = OUTPUT_FILE,
    embeddings_path: Path = MODELS_FOLDER,
) -> None:
    """Docstring."""
    logging.basicConfig(format="  %(message)s")

    extra_model = ExtraModel(models_folder=embeddings_path)
    extra_model.load_from_files()

    logger.info(f"Loading data from {input_path}")
    input_data = pd.read_csv(input_path)

    logger.info("Running `extra-model`")
    results_raw = extra_model.predict(comments=input_data.to_dict("records"))
    results = pd.DataFrame(results_raw)

    if not output_path.exists():
        logger.info(f"Creating folder {output_path}")
        output_path.mkdir(parents=True)

    logger.info(f"Saving output to {output_path / output_filename}")
    results.to_csv(output_path / output_filename, encoding="utf-8", index=False)
