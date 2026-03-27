"""Tests for CLI commands."""

import json

from typer.testing import CliRunner

from cloudclerk.cli import app

runner = CliRunner()


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "cloudclerk" in result.output
    assert "0.1.0" in result.output


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "configure" in result.output
    assert "queries" in result.output


def test_queries_help():
    result = runner.invoke(app, ["queries", "--help"])
    assert result.exit_code == 0
    assert "top" in result.output
    assert "show" in result.output


def test_queries_top_invalid_priority(monkeypatch):
    monkeypatch.setattr(
        "cloudclerk.config.require_config",
        lambda: {"auth": {"api_key": "cc_live_test"}, "server": {"url": "https://test.io"}},
    )
    result = runner.invoke(app, ["queries", "top", "--priority", "invalid"])
    assert result.exit_code == 1


def test_queries_top_json_output(monkeypatch):
    mock_data = {"results": [{"query_sha": "abc123", "estimated_cost_usd": "100.00", "priority": "high"}]}

    monkeypatch.setattr(
        "cloudclerk.commands.queries.CloudClerkClient",
        lambda: type("MockClient", (), {"list_queries": lambda self, **kw: mock_data})(),
    )

    result = runner.invoke(app, ["queries", "top", "--json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["results"][0]["query_sha"] == "abc123"


def test_queries_show_json_output(monkeypatch):
    mock_data = {"analysis": {"query_sha": "abc123", "priority": "high", "analysis_result": {"recommendations": []}}}

    monkeypatch.setattr(
        "cloudclerk.commands.queries.CloudClerkClient",
        lambda: type("MockClient", (), {"get_query": lambda self, sha: mock_data})(),
    )

    result = runner.invoke(app, ["queries", "show", "abc123", "--json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["analysis"]["query_sha"] == "abc123"
