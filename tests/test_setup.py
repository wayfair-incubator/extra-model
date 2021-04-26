import subprocess
from pathlib import Path

import pytest

from extra_model._errors import ExtraModelError
from extra_model._setup import URL, cleanup, download_file, format_file, run_subprocess
from extra_model._setup import setup as setup_extra
from extra_model._setup import unzip_file

OUTPUT = "/output"


@pytest.fixture
def subprocess_run_mock(mocker):
    # NOTE: run function in subprocess module
    return mocker.patch("subprocess.run")


@pytest.fixture
def run_subprocess_mock(mocker):
    # NOTE: our wrapper around subprocess.run
    return mocker.patch("extra_model._setup.run_subprocess")


@pytest.fixture
def input_mock(mocker):
    return mocker.patch("builtins.input", return_value="y")


@pytest.fixture
def download_file_mock(mocker):
    return mocker.patch("extra_model._setup.download_file")


@pytest.fixture
def unzip_file_mock(mocker):
    return mocker.patch("extra_model._setup.unzip_file")


@pytest.fixture
def format_file_mock(mocker):
    return mocker.patch("extra_model._setup.format_file")


@pytest.fixture
def cleanup_mock(mocker):
    return mocker.patch("extra_model._setup.cleanup")


@pytest.fixture
def create_output_path(mocker):
    """Mock for Path truediv (/) operator"""

    def _create_output_path(file_exists=True):
        output_file = mocker.Mock()
        output_file.is_file.return_value = file_exists
        output_path = mocker.MagicMock()
        output_path.__truediv__.return_value = output_file
        return output_path

    return _create_output_path


def test_setup__input_return_n__setup_functions_not_called(
    input_mock, download_file_mock, unzip_file_mock, format_file_mock, cleanup_mock
):

    input_mock.return_value = "n"

    setup_extra(OUTPUT)

    download_file_mock.assert_not_called()
    unzip_file_mock.assert_not_called()
    format_file_mock.assert_not_called()
    cleanup_mock.assert_not_called()


def test_setup__input_return_True__setup_functions_called(
    input_mock, download_file_mock, unzip_file_mock, format_file_mock, cleanup_mock
):

    input_mock.return_value = "y"

    setup_extra(OUTPUT)

    download_file_mock.assert_called_once()
    unzip_file_mock.assert_called_once()
    format_file_mock.assert_called_once()
    cleanup_mock.assert_called_once()


def test_setup__output_path_set__argument_passed_to_setup_functions(
    input_mock, download_file_mock, unzip_file_mock, format_file_mock, cleanup_mock
):

    setup_extra(OUTPUT)

    download_file_mock.assert_called_once_with(URL, OUTPUT)

    unzip_file_mock.assert_called_once_with(download_file_mock.return_value, OUTPUT)

    format_file_mock.assert_called_once_with(unzip_file_mock.return_value, OUTPUT)

    cleanup_mock.assert_called_once_with(
        [download_file_mock.return_value, unzip_file_mock.return_value]
    )


def test_download_file__output_file_found__skip_download_file(
    create_output_path, run_subprocess_mock
):

    output_path = create_output_path(file_exists=True)

    download_file(URL, output_path)

    run_subprocess_mock.assert_not_called()


def test_download_file__output_file_missing__download_file(
    create_output_path, run_subprocess_mock
):

    output_path = create_output_path(file_exists=False)

    download_file(URL, output_path)

    run_subprocess_mock.assert_called_once()


def test_unzip_file__output_file_found__skip_unzip_file(
    create_output_path, run_subprocess_mock
):

    file = Path("path/to/file.zip")
    output_path = create_output_path(file_exists=True)

    unzip_file(file, output_path)

    run_subprocess_mock.assert_not_called()


def test_unzip_file__output_file_missing__unzip_file(
    create_output_path, run_subprocess_mock
):

    file = Path("path/to/file.zip")
    output_path = create_output_path(file_exists=False)

    unzip_file(file, output_path)

    run_subprocess_mock.assert_called_once()


def test_format_file__output_file_found__skip_format_file(mocker, create_output_path):

    datapath_mock = mocker.patch("extra_model._setup.datapath")
    mocker.patch("extra_model._setup.KeyedVectors")

    file = Path("path/to/file.txt")
    output_path = create_output_path(file_exists=True)

    format_file(file, output_path)

    datapath_mock.assert_not_called()


def test_format_file__output_file_missing__format_file(mocker, create_output_path):

    datapath_mock = mocker.patch("extra_model._setup.datapath")
    mocker.patch("extra_model._setup.KeyedVectors")

    file = Path("path/to/file.txt")
    output_path = create_output_path(file_exists=False)

    format_file(file, output_path)

    datapath_mock.assert_called_once()


def test_cleanup__files_unliked(mocker):
    file = mocker.Mock()
    cleanup([file])
    file.unlink.assert_called_once()


def test_run_subprocess__subprocess_called_with_command(subprocess_run_mock):
    command = "command"
    run_subprocess([command])
    subprocess_run_mock.assert_called_once_with(command, check=True, shell=True)


def test_run_subprocess__return_code_not_zero__raise_ExtraModelError(
    subprocess_run_mock,
):
    subprocess_run_mock.side_effect = subprocess.CalledProcessError(1, "command")

    with pytest.raises(ExtraModelError, match=r"Subprocess error: ."):
        run_subprocess("command")
