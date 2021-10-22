import logging
from pathlib import Path

import pytest
from click.testing import CliRunner

from extra_model._cli import entrypoint, entrypoint_setup
from extra_model._errors import ExtraModelError


@pytest.fixture()
def cli_runner():
    return CliRunner()


@pytest.fixture
def run_mock(mocker):
    return mocker.patch("extra_model._cli.run")


@pytest.fixture
def setup_mock(mocker):
    return mocker.patch("extra_model._cli.setup")


INPUT = "/input"
OUTPUT = "/output"
OUTPUT_FILENAME = "result.csv"
EMBEDDINGS_PATH = "/embeddings"


def test_entrypoint__run_raises_no_exception__exit_code_0(cli_runner, run_mock):

    result = cli_runner.invoke(entrypoint, [INPUT], catch_exceptions=False)

    assert result.exit_code == 0


def test_entrypoint__run_raises_ExtraModelError__exit_code_1(cli_runner, run_mock):

    run_mock.side_effect = ExtraModelError

    result = cli_runner.invoke(entrypoint, [INPUT], catch_exceptions=False)

    assert result.exit_code == 1


def test_entrypoint__run_raises_unhandled_exception__exception_raised(
    cli_runner, run_mock
):

    run_mock.side_effect = Exception

    with pytest.raises(Exception):
        cli_runner.invoke(entrypoint, [INPUT], catch_exceptions=False)


def test_entrypoint__debug_set__log_level_set_to_DEBUG(cli_runner, run_mock):

    cli_runner.invoke(entrypoint, [INPUT, "--debug"], catch_exceptions=False)

    assert logging.getLogger("extra_model").level == logging.DEBUG


def test_entrypoint__all_options_are_set_and_passed_to_run(cli_runner, run_mock):
    cli_runner.invoke(
        entrypoint,
        [INPUT, "-op", OUTPUT, "-of", OUTPUT_FILENAME, "-ep", EMBEDDINGS_PATH],
        catch_exceptions=False,
    )

    run_mock.assert_called_once_with(
        Path(INPUT), Path(OUTPUT), Path(OUTPUT_FILENAME), Path(EMBEDDINGS_PATH)
    )


def test_entrypoint_setup__setup_raises_no_exception__exit_code_0(
    cli_runner, setup_mock
):

    result = cli_runner.invoke(entrypoint_setup, catch_exceptions=False)

    assert result.exit_code == 0


def test_entrypoint_setup__setup_raises_ExtraModelError__exit_code_1(
    cli_runner, setup_mock
):

    setup_mock.side_effect = ExtraModelError

    result = cli_runner.invoke(entrypoint_setup, catch_exceptions=False)

    assert result.exit_code == 1


def test_entrypoint_setup__setup_raises_unhandled_exception__exception_raised(
    cli_runner, setup_mock
):

    setup_mock.side_effect = Exception

    with pytest.raises(Exception):
        cli_runner.invoke(entrypoint_setup, catch_exceptions=False)


def test_entrypoint_setup__output_path_set__argument_passed_to_setup(
    cli_runner, setup_mock
):

    cli_runner.invoke(entrypoint_setup, [OUTPUT], catch_exceptions=False)

    setup_mock.assert_called_once_with(Path(OUTPUT))
