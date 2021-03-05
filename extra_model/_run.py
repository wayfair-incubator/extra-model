import logging
from pathlib import Path

import pandas as pd

from extra_model._models import ExtraModel

MODELS_FOLDER = "./embeddings"
OUTPUT_FILE = "result.csv"

logger = logging.getLogger(__name__)


def run(
    input_path: Path, output_path: Path, output_filename: Path = OUTPUT_FILE
) -> None:
    """Docstring."""
    logging.basicConfig(format="  %(message)s")

    extra_model = ExtraModel(models_folder=MODELS_FOLDER)
    extra_model.load_from_files()

    input_data = pd.read_csv(input_path)

    results_raw = extra_model.predict(comments=input_data.to_dict("records"))
    results = pd.DataFrame(results_raw)

    if not output_path.exists():
        output_path.mkdir(parents=True)

    results.to_csv(output_path / output_filename, encoding="utf-8", index=False)
