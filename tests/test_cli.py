import logging

import pytest
from click.testing import CliRunner

from extra_model._cli import entrypoint


@pytest.fixture()
def cli_runner():
    return CliRunner()


def test_entrypoint__debug_set__log_level_set_to_DEBUG(cli_runner):

    result = cli_runner.invoke(entrypoint, ["my_directory", "--debug"])

    assert logging.getLogger("extra_model").level == logging.DEBUG
    assert result.exit_code == 0


def test_entrypoint__setting_input_dir(cli_runner):
    result = cli_runner.invoke(entrypoint, ["my_directory"])

    assert result.exit_code == 0


def test_entrypoint__setting_custom_output_dir(cli_runner):
    result = cli_runner.invoke(entrypoint, ["my_directory", "output_dir"])

    assert result.exit_code == 0
