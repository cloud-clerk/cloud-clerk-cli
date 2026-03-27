"""Tests for display formatting helpers."""

from cloudclerk.display import format_date, format_priority, format_savings, format_usd


def test_format_usd():
    assert format_usd(1234.56) == "$1,234.56"
    assert format_usd(0) == "$0.00"
    assert format_usd(None) == "-"


def test_format_savings():
    assert format_savings(100, 500) == "$100.00 - $500.00"
    assert format_savings(None, None) == "-"


def test_format_priority_colors():
    high = format_priority("high")
    assert high.plain == "HIGH"

    medium = format_priority("medium")
    assert medium.plain == "MEDIUM"

    low = format_priority("low")
    assert low.plain == "LOW"

    none = format_priority(None)
    assert none.plain == "-"


def test_format_date():
    assert format_date("2026-03-25T14:30:00Z") == "2026-03-25"
    assert format_date(None) == "-"
    assert format_date("") == "-"
