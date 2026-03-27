"""CloudClerk CLI — BigQuery cost optimization from the terminal."""

import typer

from cloudclerk import __version__
from cloudclerk.commands.configure import configure
from cloudclerk.commands.queries import queries_app

app = typer.Typer(
    name="cloudclerk",
    help="CloudClerk CLI — BigQuery cost optimization from the terminal.",
    no_args_is_help=True,
)

app.command()(configure)
app.add_typer(queries_app, name="queries", help="Query cost analysis")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"cloudclerk {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", callback=version_callback, is_eager=True, help="Show version"),
) -> None:
    """CloudClerk CLI — BigQuery cost optimization from the terminal."""
