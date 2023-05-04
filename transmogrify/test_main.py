from typer.testing import CliRunner
from .main import app
import shlex
from pathlib import Path

runner = CliRunner()


def test_formats():
    result = runner.invoke(app, shlex.split("formats"))
    assert result.exit_code == 0
    assert "json" in result.stdout
    assert "xml" not in result.stdout


def test_convert_json_to_toml():
    result = runner.invoke(
        app, shlex.split("convert --input tests/test.json --output-format toml")
    )
    assert result.exit_code == 0
    assert result.stdout == Path("tests/test.toml").read_text()


def test_convert_get_key():
    result = runner.invoke(app, shlex.split("get-key --input tests/test.json hello"))
    assert result.exit_code == 0
    assert "world" in result.stdout
