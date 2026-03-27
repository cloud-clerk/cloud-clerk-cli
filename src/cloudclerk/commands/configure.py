"""'cloudclerk configure' command — set up API key and server URL."""

import typer
from rich.console import Console

from cloudclerk.config import DEFAULT_SERVER_URL, load_config, save_config

console = Console()


def configure() -> None:
    """Configure CloudClerk CLI with your API key and server URL."""
    console.print()
    console.print("[bold]CloudClerk CLI Configuration[/bold]")
    console.print()

    existing = load_config()
    existing_url = (existing or {}).get("server", {}).get("url", DEFAULT_SERVER_URL)

    api_key = typer.prompt("API Key", hide_input=True)

    if not api_key.startswith(("cc_live_", "cc_test_")):
        console.print("[red]Invalid API key format.[/red] Keys start with 'cc_live_' or 'cc_test_'.")
        raise typer.Exit(1)

    server_url = typer.prompt("Server URL", default=existing_url)

    path = save_config(api_key=api_key, server_url=server_url)
    console.print()
    console.print(f"[green]Configuration saved[/green] to [dim]{path}[/dim]")

    # Test connectivity
    console.print()
    console.print("[dim]Testing connection...[/dim]", end=" ")

    try:
        from cloudclerk.client import CloudClerkClient

        client = CloudClerkClient(api_key=api_key, server_url=server_url)
        client.get_latest_run()
        console.print("[green]OK[/green]")
    except SystemExit:
        # Connection error already printed by client
        console.print()
        console.print("[yellow]Configuration saved, but connection failed.[/yellow]")
        console.print("You can still use the CLI — check your server URL and API key.")
    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] {e}")
        console.print("Configuration saved, but could not verify the connection.")

    console.print()
