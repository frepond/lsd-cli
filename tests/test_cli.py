import pytest
from click.testing import CliRunner
from lsd_cli import cli


@pytest.fixture
def runner():
    return CliRunner()

def test_cli_help(runner):
    result = runner.invoke(cli.main, ['--help'])
    assert not result.exception
    assert result.exit_code == 0
    assert result.output.strip() == """Usage: lsd-cli [OPTIONS] [TENANT]

  Leapsight Semantic Dataspace Command Line Tool

Options:
  -h, --host TEXT     LSD host.
  -p, --port INTEGER  LSD port.
  --help              Show this message and exit."""
