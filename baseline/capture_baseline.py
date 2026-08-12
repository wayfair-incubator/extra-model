"""Capture a pre-migration baseline of the full extra-model pipeline.

Runs the same end-to-end path as tests/test_models.py::test_predict, but over the
whole 100-comment fixture, using the vendored small embeddings so no 2.1GB GloVe
download is needed. Output is the drift reference for the dependency migration.
"""

import logging
import os
import sys

import pandas as pd

from extra_model._models import extra_factory

logging.basicConfig(level="WARNING")

REPO = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
RESOURCES = os.path.join(REPO, "tests", "resources")


def main(output_csv):
    ExtraModel = extra_factory()
    model = ExtraModel(models_folder=RESOURCES + "/", embedding_type="small_embeddings")
    model.load_from_files()

    comments = pd.read_csv(os.path.join(RESOURCES, "100_comments.csv")).to_dict(
        "records"
    )
    result = pd.DataFrame(model.predict(comments=comments))

    # sort so the diff is stable against row-ordering changes
    result = result.sort_values(by=sorted(result.columns)).reset_index(drop=True)
    result.to_csv(output_csv, index=False)

    print(f"rows: {len(result)}")
    print(f"columns: {list(result.columns)}")
    print(f"dtypes:\n{result.dtypes}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "baseline/result-before.csv")
