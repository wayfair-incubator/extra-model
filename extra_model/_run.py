from pathlib import Path

import pandas as pd

from extra_model._models import ExtraModel

MODELS_FOLDER = "./glove_embeddings"
OUTPUT_FILE = "result.csv"


def run(input_path: Path, output_path: Path) -> None:
    """Docstring."""
    extra_model = ExtraModel(models_folder=MODELS_FOLDER)
    extra_model.load_from_files()

    input_data = pd.read_csv(input_path)

    results_raw = extra_model.predict(comments=input_data.to_dict("records"))
    results = pd.DataFrame(results_raw)

    if not output_path.exists():
        output_path.mkdir()

    results.to_csv(output_path / OUTPUT_FILE, encoding="utf-8", index=False)
