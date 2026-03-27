"""Tests for the HTTP client."""

import json

import httpx
import pytest

from cloudclerk.client import APIError, CloudClerkClient


@pytest.fixture
def mock_client(monkeypatch):
    """Create a CloudClerkClient without loading config."""
    monkeypatch.setattr(
        "cloudclerk.client.require_config",
        lambda: {"auth": {"api_key": "cc_live_test"}, "server": {"url": "https://test.cloudclerk.io"}},
    )
    return CloudClerkClient()


def test_client_sets_auth_header(mock_client):
    assert mock_client._client.headers["authorization"] == "Bearer cc_live_test"


def test_client_sets_base_url(mock_client):
    assert str(mock_client._client.base_url) == "https://test.cloudclerk.io"


def test_client_strips_trailing_slash(monkeypatch):
    monkeypatch.setattr(
        "cloudclerk.client.require_config",
        lambda: {"auth": {"api_key": "cc_live_test"}, "server": {"url": "https://test.cloudclerk.io/"}},
    )
    client = CloudClerkClient()
    assert str(client._client.base_url) == "https://test.cloudclerk.io"


def test_client_explicit_params():
    client = CloudClerkClient(api_key="cc_live_abc", server_url="https://my.server.io")
    assert client._api_key == "cc_live_abc"
    assert client._base_url == "https://my.server.io"


def test_list_queries_params(mock_client, monkeypatch):
    captured = {}

    def mock_get(self, path, params=None):
        captured["path"] = path
        captured["params"] = params
        return {"results": []}

    monkeypatch.setattr(CloudClerkClient, "get", mock_get)

    mock_client.list_queries(limit=5, priority="high")
    assert captured["path"] == "/api/v1/cost-optimization/analyses/"
    assert captured["params"]["page_size"] == 5
    assert captured["params"]["priority"] == "high"
    assert captured["params"]["ordering"] == "-estimated_cost_usd"


def test_get_query_path(mock_client, monkeypatch):
    captured = {}

    def mock_get(self, path, params=None):
        captured["path"] = path
        return {"analysis": {}}

    monkeypatch.setattr(CloudClerkClient, "get", mock_get)

    mock_client.get_query("abc123def456")
    assert captured["path"] == "/api/v1/cost-optimization/analyses/abc123def456/"
