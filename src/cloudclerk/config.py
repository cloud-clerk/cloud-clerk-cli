"""Configuration management for CloudClerk CLI.

Stores config in ~/.cloudclerk/config.toml:

    [auth]
    api_key = "cc_live_..."

    [server]
    url = "https://app.cloudclerk.io"
"""

import sys
from pathlib import Path

import tomli_w

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


DEFAULT_SERVER_URL = "https://app.cloudclerk.io"
CONFIG_DIR_NAME = ".cloudclerk"
CONFIG_FILE_NAME = "config.toml"


def get_config_dir() -> Path:
    return Path.home() / CONFIG_DIR_NAME


def get_config_path() -> Path:
    return get_config_dir() / CONFIG_FILE_NAME


def load_config() -> dict | None:
    """Load config from disk. Returns None if file doesn't exist."""
    path = get_config_path()
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return tomllib.load(f)


def save_config(api_key: str, server_url: str) -> Path:
    """Save config to disk. Creates directory if needed. Returns the config path."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "auth": {"api_key": api_key},
        "server": {"url": server_url},
    }

    path = get_config_path()
    with open(path, "wb") as f:
        tomli_w.dump(config, f)

    return path


def require_config() -> dict:
    """Load config or exit with a helpful message."""
    config = load_config()
    if config is None:
        from rich.console import Console

        console = Console(stderr=True)
        console.print("[red]Not configured.[/red] Run [bold]cloudclerk configure[/bold] first.")
        sys.exit(1)

    missing = []
    if not config.get("auth", {}).get("api_key"):
        missing.append("api_key")
    if not config.get("server", {}).get("url"):
        missing.append("server url")

    if missing:
        from rich.console import Console

        console = Console(stderr=True)
        console.print(f"[red]Config incomplete[/red] (missing: {', '.join(missing)}). Run [bold]cloudclerk configure[/bold].")
        sys.exit(1)

    return config
