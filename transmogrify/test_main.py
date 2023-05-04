from typer.testing import CliRunner

from .main import app

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["formats"])
    assert result.exit_code == 0
    assert "json" in result.stdout
    assert "xml" not in result.stdout
