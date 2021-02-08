import datetime as dt
import json
import logging
import os
import shutil
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from extra_model._adjectives import adjective_info
from extra_model._aspects import generate_aspects
from extra_model._filter import filter
from extra_model._summarize import link_aspects_to_texts, link_aspects_to_topics, qa
from extra_model._topics import get_topics
from extra_model._vectorizer import Vectorizer

CB_BASE_DIR = "/wayfair/mnt/crunch_buckets/central/data_science/extra/glove_embeddings"


logger = logging.getLogger(__name__)


class ModelBase:
    """Base class that provides file loading functionality"""

    models_folder: str
    _storage_metadata: Dict[str, str]

    def load_from_files(self):
        """Load model files"""
        # load the storage metadata info obtained when loading models from model storage
        file_name = os.path.join(self.models_folder, "metadata.json")
        storage_metadata = {}
        if os.path.isfile(file_name):
            with open(file_name) as f:
                storage_metadata = json.load(f)

            # overwrite storage_metadata for select fields
            self._storage_metadata["id"] = storage_metadata.get("id")
            self._storage_metadata["dag_id"] = storage_metadata.get("dag_id")
            self._storage_metadata["dag_run_id"] = storage_metadata.get("dag_run_id")
            self._storage_metadata["date_trained"] = storage_metadata.get(
                "date_trained"
            )
            self._storage_metadata["target_training_date"] = storage_metadata.get(
                "target_training_date"
            )
            self._storage_metadata["json_extras"] = storage_metadata.get("json_extras")


# NOTE: improve typehints!
def extra_factory(bases: Optional[Union[Any, Tuple[Any]]] = ModelBase) -> Any:
    """Factory for ExtraModel class types. Will dynamically create
    the class when called with the provided base classes

    :param bases: Base classes to be used when creating ExtraModel class
    :type bases: Class type or tuple of class types

    :return: ExtraModel class
    """

    if not isinstance(bases, tuple):
        bases = (bases,)
    bases = bases + (ExtraModelBase,)

    return type("ExtraModel", bases, {})


class ExtraModelBase:
    """Extra model class that provides an interface for
    training and predicting
    """

    is_trained = False
    models_folder = "/models"
    training_folder = "/wayfair/mnt/sql_staging/exports"

    _filenames = {
        "embeddings": "glove.840B.300d.prepro.vectors.npy",
        "prepro": "glove.840B.300d.prepro",
    }
    # there is no need for this since Extra doesn't create any artifacts
    _training_artifacts: Dict[str, str] = {}

    def __init__(
        self,
        dag_id="",
        dag_run_id="",
        models_folder=models_folder,
        embedding_type="glove.840B.300d.prepro",
    ):
        """
        Init function for ExtraModel object

        KWARGS:
            dag_id (str): Name of dag
            dag_runs_ids (str): Dag run IDs
            models_folder (str): Path to folder where model files are stored
            embedding_type (str): Name of embedding file. Default is "glove.840B.300d.prepro"
        """

        self.models_folder = models_folder
        self.embedding_type = embedding_type
        self.api_spec_names = {
            "position": "Position",
            "aspect": "Aspect",
            "descriptor": "Descriptor",
            "aspect_count": "AspectCount",
            "wordnet_node": "WordnetNode",
            "sentiment_compound_aspect": "SentimentCompound",
            "sentiment_binary_aspect": "SentimentBinary",
            "adcluster": "AdCluster",
            "source_guid": "CommentId",
            "topic": "Topic",
            "importance": "TopicImportance",
            "sentiment_compound_topic": "TopicSentimentCompound",
            "sentiment_binary_topic": "TopicSentimentBinary",
            "num_occurance": "TopicCount",
        }

        self._storage_metadata = {
            "type": "text",
            "owner": "DS EU VoC",
            "description": "Running ExtRA algorithm as a service to support Customer Feedback Hub use-cases",
            "display_name": "extra-model",
            "features": {},
            "hyperparameters": {},
            "dag_id": dag_id,
            "dag_run_id": dag_run_id,
            "is_scheduled_creation": False,
            "date_trained": str(dt.date.today()),
            "target_training_date": str(dt.date.today()),
            "json_extras": {"classification_report_json": ""},
        }
        for key in self._filenames:
            self._storage_metadata[key] = {}

    def storage_metadata(self):
        return self._storage_metadata

    def load_from_files(self):
        super().load_from_files()
        self.vectorizer = Vectorizer(
            os.path.join(self.models_folder, self.embedding_type)
        )
        self.is_trained = True

    def train(self):
        for key, filename in self._filenames.items():
            logger.debug(f"Downloading {key}")
            shutil.copyfile(
                src=os.path.join(CB_BASE_DIR, filename),
                dst=os.path.join(self.models_folder, filename),
            )
        self.is_trained = True

    def predict(self, comments: List[Dict[str, str]]) -> List[Dict]:
        if not self.is_trained:
            raise RuntimeError("Extra must be trained before you can predict!")
        dataframe_texts = pd.DataFrame(comments)
        dataframe_texts.rename(
            {"CommentId": "source_guid"}, axis="columns", inplace=True
        )
        dataframe_texts = filter(dataframe_texts)
        dataframe_aspects = generate_aspects(dataframe_texts)

        if dataframe_aspects.empty:
            raise ValueError(
                "Input dataset doesn't contain valid aspects, stopping the algorithm"
            )

        # aggregate and abstract aspects into topics
        dataframe_topics = get_topics(dataframe_aspects, self.vectorizer)
        dataframe_topics, dataframe_aspects = adjective_info(
            dataframe_topics, dataframe_aspects, self.vectorizer
        )
        dataframe_aspects = link_aspects_to_topics(dataframe_aspects, dataframe_topics)
        dataframe_aspects = link_aspects_to_texts(dataframe_aspects, dataframe_texts)

        # do some extra book-keeping if debug-level is set low enough
        if logger.isEnabledFor(20):
            qa(dataframe_texts, dataframe_aspects, dataframe_topics)

        # write output_tables, after dropping auxilliary information
        dataframe_topics.loc[:, "num_occurance"] = dataframe_topics["rawnums"].apply(
            lambda counts: sum(counts)
        )
        dataframe_topics = dataframe_topics[
            [
                "topicID",
                "topic",
                "importance",
                "sentiment_compound",
                "sentiment_binary",
                "num_occurance",
            ]
        ]

        dataframe_aspects.dropna(axis=0, inplace=True)
        dataframe_aspects["topicID"] = dataframe_aspects["topicID"].astype(int)

        output = dataframe_aspects.merge(
            dataframe_topics, on="topicID", suffixes=("_aspect", "_topic")
        )
        return standardize_output(output, names=self.api_spec_names).to_dict("records")


def standardize_output(data: pd.DataFrame, names: dict) -> pd.DataFrame:
    """
    Helper function to ensure that:
    a) only required columns are returned and
    b) they are named according to spec.

    :param data: input dataframe.
    :param names: dictionary to standardize output to API spec.
    :return: renamed dataframe.
    """
    return data[list(names.keys())].rename(columns=names)
