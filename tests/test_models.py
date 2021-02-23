import json
import os

import pandas as pd
import pytest

from extra_model._models import ExtraModelBase, ModelBase, extra_factory

ExtraModel = extra_factory()


class MyCustomBase:
    pass


def test_extra_factory__no_custom_bases_passed__class_has_ModelBase_as_parent():

    Model = extra_factory()

    assert issubclass(Model, ModelBase)


def test_extra_factory__no_custom_bases_passed__class_has_ExtraModelBase_as_parent():

    Model = extra_factory()

    assert issubclass(Model, ExtraModelBase)


def test_extra_factory__custom_bases_passed__class_has_custom_base_as_parent():

    Model = extra_factory(MyCustomBase)

    assert issubclass(Model, MyCustomBase)


def test_extra_factory__multiple_custom_bases_passed__class_has_all_custom_bases_as_parents():
    class MyOtherCustomBase:
        pass

    Model = extra_factory((MyCustomBase, MyOtherCustomBase))

    assert issubclass(Model, MyCustomBase)
    assert issubclass(Model, MyOtherCustomBase)


def test_extra_factory__custom_bases_passed__class_does_not_have_ModelBase_as_parent():

    Model = extra_factory(MyCustomBase)

    assert not issubclass(Model, ModelBase)


def test_extra_factory__custom_bases_passed__class_has_extraModelBase_as_parent():

    Model = extra_factory(MyCustomBase)

    assert issubclass(Model, ExtraModelBase)


@pytest.fixture
def tmp_untrained_res_models_folder_ExtraModel():
    resources_folder = os.path.dirname(os.path.realpath(__file__)) + "/resources/"
    untrained = ExtraModel(
        models_folder=resources_folder, embedding_type="small_embeddings"
    )
    return untrained


@pytest.fixture
def tmp_untrained_tmp_models_folder_ExtraModel(tmpdir_factory):
    tmp_folder = tmpdir_factory.mktemp("tmp_models")
    untrained = ExtraModel(models_folder=tmp_folder, embedding_type="small_embeddings")
    yield untrained


@pytest.fixture
def tmp_trained_ExtraModel():
    resources_folder = os.path.dirname(os.path.realpath(__file__)) + "/resources/"
    trained = ExtraModel(
        models_folder=resources_folder, embedding_type="small_embeddings"
    )
    trained.load_from_files()
    return trained


@pytest.fixture
def test_comments():
    input_ = pd.read_csv("./tests/resources/100_comments.csv")
    return input_.to_dict("records")


def test_create(tmp_untrained_tmp_models_folder_ExtraModel, test_comments):
    # test for initialization
    assert not tmp_untrained_tmp_models_folder_ExtraModel.is_trained
    # test that prediction fails without loading
    with pytest.raises(RuntimeError):
        tmp_untrained_tmp_models_folder_ExtraModel.predict(comments=test_comments)
    # for filekey in tmp_untrained_tmp_models_folder_ExtraModel.filenames:
    #     assert filekey in tmp_untrained_tmp_models_folder_ExtraModel.storage_metadata()


def test_load_from_files(tmp_untrained_res_models_folder_ExtraModel):
    assert not tmp_untrained_res_models_folder_ExtraModel.is_trained
    tmp_untrained_res_models_folder_ExtraModel.load_from_files()
    assert tmp_untrained_res_models_folder_ExtraModel.is_trained


def test_predict(tmp_trained_ExtraModel, test_comments):
    # Extra is an unsupervised algorithm, so not possible to guarantee certain output
    res = tmp_trained_ExtraModel.predict(comments=test_comments)
    res_names = set(pd.DataFrame(res).columns.values)
    required_names = set(tmp_trained_ExtraModel.api_spec_names.values())
    assert len(required_names.difference(res_names)) == len(
        res_names.difference(required_names)
    )
    try:
        json.dumps(res)
    except Exception:
        pytest.fail("Serialization failed")

    # extra should fail with correct error for this input
    test_comments_1 = [
        {"CommentId": 1, "Comments": "Hey ho"},
        {"CommentId": 2, "Comments": "comment number two"},
    ]
    with pytest.raises(ValueError):
        tmp_trained_ExtraModel.predict(comments=test_comments_1)

    # extra should succeed with this input
    test_comments_2 = [
        {
            "CommentId": 986,
            "Comments": "The problem I have is that they charge $11.99 for a sandwich that is no bigger than a Subway sub (which offers better and more amount of vegetables).",
        },
        {"CommentId": 860, "Comments": "Worst food/service I've had in a while"},
    ]
    res = tmp_trained_ExtraModel.predict(comments=test_comments_2)
    assert len(res) > 0
