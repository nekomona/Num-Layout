"""Local test configuration and Git-ignored report destinations."""

import os
from pathlib import Path
import re


def setting(name, default=""):
    value = os.environ.get(name, default)
    if value and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", value):
        raise ValueError(f"{name} must be a simple library, cell, or layer name")
    return value


LIB = setting("VBN_TEST_LIB", "NUMERIC_ASSIST_TESTS")
LAYER = setting("VBN_TEST_LAYER", "M1")
PCELL_LIB = setting("VBN_TEST_PCELL_LIB")
PCELL_CELL = setting("VBN_TEST_PCELL_CELL")


def artifact_path(name):
    directory = Path(__file__).resolve().parents[1] / "artifacts" / "reports"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / name
