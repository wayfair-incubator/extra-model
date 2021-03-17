import pytest

from extra_model._run import run


@pytest.fixture
def extra_model_mock(mocker):
    return mocker.patch("extra_model._run.ExtraModel")


@pytest.fixture
def pandas_mock(mocker):
    return mocker.patch("extra_model._run.pd")


def output_path(mocker):
    return mocker.Mock()


def test_run__csv_created(mocker, extra_model_mock, pandas_mock):

    run(mocker.MagicMock(), mocker.MagicMock())

    assert extra_model_mock.called
    assert pandas_mock.DataFrame.called
    assert pandas_mock.DataFrame.return_value.to_csv.called


def test_run__output_path_exists__output_path_not_created(
    mocker, extra_model_mock, pandas_mock
):

    output_path = mocker.MagicMock()
    output_path.exists.return_value = True

    run(mocker.MagicMock(), output_path)

    assert output_path.exists.called
    assert not output_path.mkdir.called


def test_run__output_path_does_not_exist__output_path_created(
    mocker, extra_model_mock, pandas_mock
):

    output_path = mocker.MagicMock()
    output_path.exists.return_value = False

    run(mocker.MagicMock(), output_path)

    assert output_path.exists.called
    assert output_path.mkdir.called
