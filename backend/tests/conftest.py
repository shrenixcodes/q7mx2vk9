from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> list[dict]:
    with (FIXTURES_DIR / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def fuelhh_wind_sample() -> list[dict]:
    return load_fixture("fuelhh_wind_sample_2026-01-10.json")


@pytest.fixture
def fuelhh_mixed_fuel_sample() -> list[dict]:
    return load_fixture("fuelhh_mixed_fuel_sample_2026-01-10.json")


@pytest.fixture
def windfor_two_vintages_sample() -> list[dict]:
    return load_fixture("windfor_two_vintages_sample_2026-01-10.json")
