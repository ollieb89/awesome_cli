"""
Tests for CLI commands.
"""
from typer.testing import CliRunner
from awesome_cli.cli import app
from awesome_cli import __version__

runner = CliRunner()

def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout

def test_init_command():
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Initializing" in result.stdout

def test_run_command():
    result = runner.invoke(app, ["run", "--name", "integration_test"])
    assert result.exit_code == 0
    assert "integration_test" in result.stdout
    assert "Success" in result.stdout

def test_run_command_verbose():
    result = runner.invoke(app, ["run", "--verbose"])
    assert result.exit_code == 0
    assert "Loaded settings" in result.stdout
