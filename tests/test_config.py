"""Tests for config management."""

from pathlib import Path

from cloudclerk.config import get_config_path, load_config, save_config


def test_save_and_load_config(tmp_path, monkeypatch):
    monkeypatch.setattr("cloudclerk.config.get_config_dir", lambda: tmp_path)
    monkeypatch.setattr("cloudclerk.config.get_config_path", lambda: tmp_path / "config.toml")

    path = save_config(api_key="cc_live_testkey123", server_url="https://example.com")
    assert path.exists()

    config = load_config()
    assert config["auth"]["api_key"] == "cc_live_testkey123"
    assert config["server"]["url"] == "https://example.com"


def test_load_config_returns_none_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("cloudclerk.config.get_config_path", lambda: tmp_path / "nonexistent.toml")
    assert load_config() is None


def test_require_config_exits_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("cloudclerk.config.get_config_path", lambda: tmp_path / "nonexistent.toml")

    import pytest

    with pytest.raises(SystemExit):
        from cloudclerk.config import require_config

        require_config()


def test_get_config_path_is_in_home():
    path = get_config_path()
    assert ".cloudclerk" in str(path)
    assert path.name == "config.toml"
