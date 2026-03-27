"""Rich display helpers for CloudClerk CLI output."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


console = Console()

PRIORITY_COLORS = {
    "high": "red",
    "medium": "yellow",
    "low": "green",
}


def format_usd(value) -> str:
    """Format a numeric value as USD."""
    if value is None:
        return "-"
    return f"${float(value):,.2f}"


def format_savings(min_val, max_val) -> str:
    """Format a savings range as '$X - $Y'."""
    if min_val is None and max_val is None:
        return "-"
    return f"{format_usd(min_val)} - {format_usd(max_val)}"


def format_priority(priority: str | None) -> Text:
    """Return a colored priority label."""
    if not priority:
        return Text("-")
    color = PRIORITY_COLORS.get(priority.lower(), "white")
    return Text(priority.upper(), style=f"bold {color}")


def format_date(date_str: str | None) -> str:
    """Format an ISO datetime string to a short date."""
    if not date_str:
        return "-"
    return date_str[:10]


def render_queries_table(data: dict) -> None:
    """Render a table of query analyses."""
    results = data.get("results", [])

    if not results:
        console.print("[dim]No query analyses found.[/dim]")
        return

    table = Table(title="Most Expensive Queries", show_lines=True, expand=False)
    table.add_column("#", justify="right", width=3)
    table.add_column("Priority", justify="center", width=8)
    table.add_column("Cost", justify="right", width=12)
    table.add_column("Savings", justify="right", width=18)
    table.add_column("Run Date", width=10)

    shas = []
    for i, row in enumerate(results, 1):
        sha = row.get("query_sha") or ""
        shas.append(sha)
        table.add_row(
            str(i),
            format_priority(row.get("priority")),
            format_usd(row.get("estimated_cost_usd")),
            format_savings(row.get("potential_savings_min_usd"), row.get("potential_savings_max_usd")),
            format_date(row.get("run_created_at") or row.get("created_at")),
        )

    console.print(table)

    # Print SHAs below the table so they're fully copy-pasteable
    console.print()
    console.print("[bold]Query SHAs[/bold] (use with [bold]cloudclerk queries show <sha>[/bold]):")
    for i, sha in enumerate(shas, 1):
        console.print(f"  {i}. {sha}")
    console.print()


def render_query_detail(data: dict) -> None:
    """Render full details for a single query analysis."""
    analysis = data.get("analysis", data)

    query_sha = analysis.get("query_sha", "unknown")
    priority = analysis.get("priority")
    cost = analysis.get("estimated_cost_usd")
    savings_min = analysis.get("potential_savings_min_usd")
    savings_max = analysis.get("potential_savings_max_usd")
    created = format_date(analysis.get("run_created_at") or analysis.get("created_at"))

    # Header
    console.print()
    console.print(f"[bold]Query Analysis:[/bold] {query_sha}")
    console.print("=" * 50)
    console.print()

    # Summary info
    info_lines = [
        f"[bold]Priority:[/bold]          {format_priority(priority)}",
        f"[bold]Estimated Cost:[/bold]    {format_usd(cost)}",
        f"[bold]Potential Savings:[/bold] {format_savings(savings_min, savings_max)}",
        f"[bold]Analyzed:[/bold]          {created}",
    ]
    for line in info_lines:
        console.print(line)

    # Query execution context from query_data
    query_data = analysis.get("query_data")
    if query_data:
        _render_query_context(query_data)

    # Query pattern (the actual SQL)
    if query_data:
        _render_query_pattern(query_data)

    # Recommendations from analysis_result
    analysis_result = analysis.get("analysis_result")
    if analysis_result:
        _render_recommendations(analysis_result)
        _render_issues(analysis_result)

    console.print()


def _format_bytes(num_bytes) -> str:
    """Format bytes into a human-readable string."""
    if num_bytes is None:
        return "-"
    num = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if abs(num) < 1024:
            return f"{num:,.1f} {unit}"
        num /= 1024
    return f"{num:,.1f} EB"


def _render_query_context(query_data: dict) -> None:
    """Render execution context from query_data."""
    lines = []

    execution_count = query_data.get("execution_count")
    if execution_count is not None:
        lines.append(f"  [bold]Executions:[/bold]       {execution_count:,}")

    statement_type = query_data.get("statement_type")
    if statement_type:
        lines.append(f"  [bold]Statement Type:[/bold]  {statement_type}")

    distinct_users = query_data.get("distinct_users")
    if distinct_users is not None:
        lines.append(f"  [bold]Distinct Users:[/bold]  {distinct_users}")

    bytes_billed = query_data.get("sum_bytes_billed")
    if bytes_billed is not None:
        lines.append(f"  [bold]Total Bytes Billed:[/bold] {_format_bytes(bytes_billed)}")

    first_seen = query_data.get("first_seen")
    last_seen = query_data.get("last_seen")
    if first_seen and last_seen:
        lines.append(f"  [bold]Observed:[/bold]        {first_seen} to {last_seen}")

    tables = query_data.get("referenced_tables", [])
    if tables:
        lines.append(f"  [bold]Referenced Tables:[/bold]")
        for t in tables:
            lines.append(f"    - {t}")

    dest = query_data.get("destination_table")
    if dest:
        lines.append(f"  [bold]Destination:[/bold]     {dest}")

    if lines:
        console.print()
        console.print(Panel("\n".join(lines), title="Query Context", border_style="cyan"))


def _render_recommendations(analysis_result: dict) -> None:
    """Render the recommendations section."""
    recommendations = analysis_result.get("recommendations", [])
    if not recommendations:
        return

    console.print()
    lines = []
    for i, rec in enumerate(recommendations, 1):
        if isinstance(rec, dict):
            action = rec.get("action") or rec.get("title") or rec.get("recommendation", "")
            description = rec.get("description", "")
            savings = rec.get("estimated_savings_usd", "")
            sql = rec.get("sql_example", "")

            lines.append(f"  [bold green]{i}. {action}[/bold green]")
            if description:
                lines.append(f"     {description}")
            if savings:
                lines.append(f"     [dim]Estimated savings: {savings}[/dim]")
            if sql:
                lines.append(f"     [blue]SQL: {sql}[/blue]")
            lines.append("")
        else:
            lines.append(f"  [bold]{i}.[/bold] {rec}")
            lines.append("")

    console.print(Panel("\n".join(lines).rstrip(), title="Recommendations", border_style="green"))


def _render_issues(analysis_result: dict) -> None:
    """Render the issues section."""
    issues = analysis_result.get("issues", [])
    if not issues:
        return

    lines = []
    for i, issue in enumerate(issues, 1):
        if isinstance(issue, dict):
            issue_type = issue.get("type", "")
            severity = issue.get("severity", "")
            description = issue.get("description", "")
            impact = issue.get("impact_estimate", "")

            color = PRIORITY_COLORS.get(severity.lower(), "white")
            label = f"[{color}][{severity.upper()}][/{color}]" if severity else ""
            type_label = issue_type.replace("_", " ").title() if issue_type else "Issue"

            lines.append(f"  [bold]{i}. {type_label}[/bold] {label}")
            if description:
                lines.append(f"     {description}")
            if impact:
                lines.append(f"     [dim]Impact: {impact}[/dim]")
            lines.append("")
        else:
            lines.append(f"  [bold]{i}.[/bold] {issue}")
            lines.append("")

    console.print(Panel("\n".join(lines).rstrip(), title="Issues Found", border_style="yellow"))


def _render_query_pattern(query_data: dict) -> None:
    """Render the query pattern section."""
    # query_data is a JSON blob from ClickHouse — try common field names
    query_text = (
        query_data.get("query")
        or query_data.get("query_text")
        or query_data.get("parameterized_query")
        or query_data.get("query_pattern")
    )
    if not query_text:
        return

    # Truncate very long queries
    if len(query_text) > 1000:
        query_text = query_text[:1000] + "\n  ... (truncated)"

    console.print()
    console.print(Panel(query_text, title="Query Pattern", border_style="blue"))
