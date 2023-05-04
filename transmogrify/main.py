import typer
from enum import Enum
from pathlib import Path
from typing_extensions import Annotated
from typing import Optional
import json
import toml
import yaml
import sys
import io


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

    def load(self, file: io.IOBase) -> object:
        pass

    def dump(self, file: io.IOBase, data: object):
        pass

    @classmethod
    def converter(cls, format: Format):
        converters = {
            Format.json: JSONConverter,
            Format.toml: TOMLConverter,
            Format.yaml: YAMLConverter,
        }
        converter = converters[format]()
        if not converter:
            raise ValueError(f"Unknown format {format}")
        return converter


class JSONConverter(Converter):
    def load(self, file: io.IOBase) -> object:
        return json.load(file)

    def dump(self, file: io.IOBase, data: object):
        json.dump(data, file)


class YAMLConverter(Converter):
    def load(self, file: io.IOBase) -> object:
        return yaml.load(file, Loader=yaml.FullLoader)

    def dump(self, file: io.IOBase, data: object):
        yaml.dump(data, file)


class TOMLConverter(Converter):
    def load(self, file: io.IOBase) -> object:
        return toml.load(file)

    def dump(self, file: io.IOBase, data: object):
        toml.dump(data, file)


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
    output: Annotated[
        Optional[Path], typer.Option("--output", "-o", allow_dash=True)
    ] = Path("-"),
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

    if input == Path("-"):
        input_file = sys.stdin
    else:
        input_file = open(input, "r")

    if output == Path("-"):
        output_file = sys.stdout
    else:
        output_file = open(output, "w")

    data = loader.load(input_file)
    dumper.dump(output_file, data)


@app.command()
def formats():
    print(", ".join([e.value for e in Format]))


@app.command()
def get_key(
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
    input_format: Annotated[Format, typer.Option("--input-format", "-F")] = None,
    key: Annotated[str, typer.Argument(...)] = None,
):
    if input_format is None:
        input_format = Format.format_for_path(input)
        if input_format is None:
            raise ValueError("Could not determine input format")
    loader = Converter.converter(input_format)

    if input == Path("-"):
        input_file = sys.stdin
    else:
        input_file = open(input, "r")

    data = loader.load(input_file)
    print(data[key])


if __name__ == "__main__":
    app()
