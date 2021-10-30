import logging
from pathlib import Path

import pandas as pd

from extra_model._errors import ExtraModelError
from extra_model._models import ExtraModel

MODELS_FOLDER = Path("./embeddings")
OUTPUT_FILE = Path("result.csv")

logger = logging.getLogger(__name__)


def check_input_structure(df):
    if not {"CommentId", "Comments"}.issubset(df.columns):
        raise ExtraModelError(
            f"Input columns must include `CommentId` and `Comments`, \
        but got {df.columns.to_list()} instead"
        )


def build_model_and_predict(
    embeddings_path: Path,
    df: pd.core.frame.DataFrame,
):
    extra_model = ExtraModel(models_folder=embeddings_path)
    extra_model.load_from_files()
    logger.info("Running `extra-model`")
    results_raw = extra_model.predict(comments=df.to_dict("records"))
    results = pd.DataFrame(results_raw)
    return results


def run(
    input_path: Path,
    output_path: Path,
    output_filename: Path = OUTPUT_FILE,
    embeddings_path: Path = MODELS_FOLDER,
) -> None:
    """Docstring."""
    logging.basicConfig(format="  %(message)s")

    logger.info(f"Loading data from {input_path}")
    input_data = pd.read_csv(input_path)

    check_input_structure(input_data)
    results = build_model_and_predict(embeddings_path, input_data)

    if not output_path.exists():
        logger.info(f"Creating folder {output_path}")
        output_path.mkdir(parents=True)

    logger.info(f"Saving output to {output_path / output_filename}")
    results.to_csv(output_path / output_filename, encoding="utf-8", index=False)


def run_from_dataframe(
    input_df: pd.core.frame.DataFrame,
    embeddings_path: Path = MODELS_FOLDER,
) -> None:
    """
    :param input_df: is a dataframe with with 2 columns: CommentId and Comments.
    :param embeddings_path: path to the embeddings files
    :return: dataframe of the extramodel results
    """
    logging.basicConfig(format="  %(message)s")

    extra_model = ExtraModel(models_folder=embeddings_path)
    extra_model.load_from_files()

    check_input_structure(input_df)
    results = build_model_and_predict(embeddings_path, input_df)

    logger.info(f"Returning results")
    return results
