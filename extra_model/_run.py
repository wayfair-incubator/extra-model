import logging
from pathlib import Path

import pandas as pd

from extra_model._errors import ExtraModelError
from extra_model._models import ExtraModel

MODELS_FOLDER = Path("./embeddings")
OUTPUT_FILE = Path("result.csv")

logger = logging.getLogger(__name__)


def run(
    input_path,
    output_path: Path = None,
    is_dataframe: bool = False,
    output_filename: Path = OUTPUT_FILE,
    embeddings_path: Path = MODELS_FOLDER,
) -> None:
    """
    :param input_path: is a dataframe or a path to .csv with with 2 columns: CommentId and Comments.
    :param embeddings_path: path to the embeddings files
    :param is_dataframe: boolean to set input_path to be used as dataframe instead of Path
    :param output_path: path to save the output .csv
    :param output_filename: filename of the output .csv to be generated
    :return: dataframe of the extramodel results if is_dataframe is True else return None
    """
    logging.basicConfig(format="  %(message)s")

    extra_model = ExtraModel(models_folder=embeddings_path)
    extra_model.load_from_files()

    logger.info(f"Loading data from {input_path}")

    if is_dataframe == False:
        input_data = pd.read_csv(input_path)
    else:
        input_data = input_path

    if not {"CommentId", "Comments"}.issubset(input_data.columns):
        raise ExtraModelError(
            f"Input columns must include `CommentId` and `Comments`, \
        but got {input_data.columns.to_list()} instead"
        )

    logger.info("Running `extra-model`")
    results_raw = extra_model.predict(comments=input_data.to_dict("records"))
    results = pd.DataFrame(results_raw)

    if is_dataframe == True:
        logger.info(f"Returning results")
        return results
    else:
        if output_path and not output_path.exists():
            logger.info(f"Creating folder {output_path}")
            output_path.mkdir(parents=True)

        if output_path and output_filename:
            logger.info(f"Saving output to {output_path / output_filename}")
            results.to_csv(output_path / output_filename, encoding="utf-8", index=False)
