# CloudClerk CLI

BigQuery cost optimization from the terminal. Analyze your most expensive queries and get actionable recommendations to reduce costs.

## Install

```bash
pipx install cloudclerk
```

Or with `uv`:

```bash
uv tool install cloudclerk
```

## Quick Start

```bash
# 1. Configure with your API key (from the CloudClerk dashboard)
cloudclerk configure

# 2. See your most expensive queries
cloudclerk queries top

# 3. Get details and recommendations for a specific query
cloudclerk queries show <query_sha>
```

## Commands

| Command | Description |
|---|---|
| `cloudclerk configure` | Set API key and server URL |
| `cloudclerk queries top` | List most expensive queries by cost |
| `cloudclerk queries show <sha>` | Full analysis: context, recommendations, issues |

## Options

```bash
cloudclerk queries top --limit 20          # Show top 20
cloudclerk queries top --priority high     # Filter by priority (high/medium/low)
cloudclerk queries top --json              # Raw JSON for piping
cloudclerk queries show <sha> --json       # Raw JSON for piping
cloudclerk --version                       # Show version
```

## What You Get

**`queries top`** - A ranked table of your most expensive queries with cost, savings potential, and priority.

**`queries show`** - Full detail for a single query:
- Query context (executions, bytes billed, referenced tables, date range)
- The actual SQL pattern
- Actionable recommendations with estimated savings and SQL examples
- Issues found with severity ratings

## Authentication

API keys are generated from the CloudClerk dashboard. Keys are prefixed with `cc_live_` and scoped to your organization.

Configuration is stored in `~/.cloudclerk/config.toml`.

## Requirements

- Python 3.10+
- A CloudClerk account with API key access

## Development

```bash
git clone https://github.com/numia-xyz/cloudclerk-cli.git
cd cloudclerk-cli
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest -v
```

## License

MIT
