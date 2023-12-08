import pytest


def format_float(f: float) -> str:
    return format(f, ",.2f").replace(",", " ").replace(".00", "")


def test_format():
    assert format_float(1.2345) == "1.23"
    assert format_float(1.2) == "1.20"
    assert format_float(1) == "1"
    assert format_float(1000000) == "1 000 000"
    assert format_float(1000000.1) == "1 000 000.10"
