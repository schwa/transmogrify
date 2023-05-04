import typer
from enum import Enum
from pathlib import Path
from typing_extensions import Annotated
from typing import Optional
import json
import toml
import yaml
import sys

app = typer.Typer()


class Format(str, Enum):
    json = "json"
    toml = "toml"
    yaml = "yaml"

    @classmethod
    def format_for_path(cls, path: Path) -> str:
        formats_by_extension = {
            ".json": Format.json,
            ".toml": Format.toml,
            ".yaml": Format.yaml,
            ".yml": Format.yaml,
        }
        return formats_by_extension[path.suffix]


class Converter:
    def __init__(self):
        pass

    def load(self, path: Path) -> object:
        pass

    def dump(self, path: Path, data: object):
        pass

    @classmethod
    def converter(cls, format: Format):
        if format == Format.csv:
            return CSVConverter()
        elif format == Format.json:
            return JSONConverter()
        elif format == Format.toml:
            return TOMLConverter()
        elif format == Format.yaml:
            return YAMLConverter()
        else:
            raise ValueError(f"Unknown format {format}")


class JSONConverter(Converter):
    def load(self, path: Path) -> object:
        if path == Path("-"):
            return json.load(sys.stdin)
        else:
            with open(path) as f:
                return json.load(f)

    def dump(self, path: Path, data: object):
        if path == Path("-"):
            json.dump(data, sys.stdout)
        else:
            with open(path, "w") as f:
                json.dump(data, f)


class YAMLConverter(Converter):
    def load(self, path: Path) -> object:
        if path == Path("-"):
            return yaml.load(sys.stdin, Loader=yaml.FullLoader)
        else:
            with open(path) as f:
                return yaml.load(f, Loader=yaml.FullLoader)

    def dump(self, path: Path, data: object):
        if path == Path("-"):
            yaml.dump(data, sys.stdout)
        else:
            with open(path, "w") as f:
                yaml.dump(data, f)


class TOMLConverter(Converter):
    def load(self, path: Path) -> object:
        if path == Path("-"):
            return toml.load(sys.stdin)
        else:
            with open(path) as f:
                return toml.load(f)

    def dump(self, path: Path, data: object):
        if path == Path("-"):
            toml.dump(data, sys.stdout)
        else:
            with open(path, "w") as f:
                toml.dump(data, f)


@app.command()
def convert(
    input: Annotated[
        Optional[Path],
        typer.Option(
            "--input",
            "-i",
            file_okay=True,
            dir_okay=False,
            readable=True,
            allow_dash=True,
        ),
    ] = Path("-"),
    output: Annotated[Optional[Path], typer.Option("--output", "-o")] = Path("-"),
    input_format: Annotated[Format, typer.Option("--input-format", "-F")] = None,
    output_format: Annotated[Format, typer.Option("--output-format", "-f")] = None,
):
    if input_format is None:
        input_format = Format.format_for_path(input)
        if input_format is None:
            raise ValueError("Could not determine input format")
    if output_format is None:
        output_format = Format.format_for_path(output)
        if output_format is None:
            raise ValueError("Could not determine output format")
    loader = Converter.converter(input_format)
    dumper = Converter.converter(output_format)
    data = loader.load(input)
    dumper.dump(output, data)


@app.command()
def formats():
    print(", ".join([e.value for e in Format]))


if __name__ == "__main__":
    app()
