import pandas as pd
import pytest

from extra_model._errors import ExtraModelError
from extra_model._run import run, run_from_dataframe


@pytest.fixture
def extra_model_mock(mocker):
    return mocker.patch("extra_model._run.ExtraModel")


@pytest.fixture
def pandas_mock(mocker):
    return mocker.patch("extra_model._run.pd")


def output_path(mocker):
    return mocker.Mock()


def test_run__csv_created(mocker, extra_model_mock, pandas_mock):
    pandas_mock.read_csv.return_value = pd.DataFrame(
        data=[[1, 2], ["test comment", "test comment 2"]],
        columns=["CommentId", "Comments"],
    )
    run(mocker.MagicMock(), mocker.MagicMock())

    assert extra_model_mock.called
    assert pandas_mock.DataFrame.called
    assert pandas_mock.DataFrame.return_value.to_csv.called


def test_run__output_path_exists__output_path_not_created(
    mocker, extra_model_mock, pandas_mock
):
    pandas_mock.read_csv.return_value = pd.DataFrame(
        data=[[1, 2], ["test comment", "test comment 2"]],
        columns=["CommentId", "Comments"],
    )
    output_path = mocker.MagicMock()
    output_path.exists.return_value = True

    run(mocker.MagicMock(), output_path)

    assert output_path.exists.called
    assert not output_path.mkdir.called


def test_run__output_path_does_not_exist__output_path_created(
    mocker, extra_model_mock, pandas_mock
):
    pandas_mock.read_csv.return_value = pd.DataFrame(
        data=[[1, 2], ["test comment", "test comment 2"]],
        columns=["CommentId", "Comments"],
    )
    output_path = mocker.MagicMock()
    output_path.exists.return_value = False

    run(mocker.MagicMock(), output_path)

    assert output_path.exists.called
    assert output_path.mkdir.called


def test_run__wrong_input_raises_error(mocker, extra_model_mock, pandas_mock):
    pandas_mock.read_csv.return_value = pd.DataFrame(
        data=[[1]],
        columns=["wrong_column_1"],
    )

    with pytest.raises(ExtraModelError, match="wrong_column_1"):
        run(mocker.MagicMock(), mocker.MagicMock())


def test_run__run_from_dataframe(mocker, extra_model_mock, pandas_mock):
    df = pd.DataFrame(
        data=[[1, "test comment"], [2, "test comment 2"]],
        columns=["CommentId", "Comments"],
    )
    run_from_dataframe(df)
    assert extra_model_mock.called
    assert pandas_mock.DataFrame.called


def test_run_from_dataframe__wrong_input_raises_error(
    mocker, extra_model_mock, pandas_mock
):
    df = pd.DataFrame(
        data=[[1]],
        columns=["wrong_column_1"],
    )

    with pytest.raises(ExtraModelError, match="wrong_column_1"):
        run_from_dataframe(df)
