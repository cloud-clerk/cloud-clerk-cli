"""'cloudclerk queries' commands — list and inspect expensive BigQuery queries."""

import json
import sys
from typing import Optional

import typer
from rich.console import Console

from cloudclerk.client import APIError, CloudClerkClient
from cloudclerk.display import render_queries_table, render_query_detail

console = Console(stderr=True)

queries_app = typer.Typer(help="Query cost analysis", no_args_is_help=True)


@queries_app.command("top")
def queries_top(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of queries to show"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="Filter by priority: high, medium, low"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output raw JSON"),
) -> None:
    """Show the most expensive queries, ranked by cost."""
    if priority and priority.lower() not in ("high", "medium", "low"):
        console.print("[red]Invalid priority.[/red] Use: high, medium, low")
        raise typer.Exit(1)

    try:
        client = CloudClerkClient()
        data = client.list_queries(limit=limit, priority=priority)
    except APIError as e:
        console.print(f"[red]Error:[/red] {e.detail}")
        raise typer.Exit(1)

    if output_json:
        typer.echo(json.dumps(data, indent=2))
    else:
        render_queries_table(data)


@queries_app.command("show")
def queries_show(
    query_sha: str = typer.Argument(help="The query SHA to inspect (from 'queries top' output)"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output raw JSON"),
) -> None:
    """Show full details and recommendations for a specific query."""
    try:
        client = CloudClerkClient()
        data = client.get_query(query_sha)
    except APIError as e:
        if e.status_code == 404:
            console.print(f"[red]Query not found:[/red] {query_sha}")
            console.print("[dim]Use 'cloudclerk queries top' to see available query SHAs.[/dim]")
        else:
            console.print(f"[red]Error:[/red] {e.detail}")
        raise typer.Exit(1)

    if output_json:
        typer.echo(json.dumps(data, indent=2))
    else:
        render_query_detail(data)
