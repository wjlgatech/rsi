"""Shared helpers for the rsi spec-as-data scripts (build_readme / validate / build_graph).

One place for the data-dir paths, the YAML loader, and markdown escaping — so the
scripts stop each redefining their own copy. Mirrors FM-os's `fmos` helper.
"""
from __future__ import annotations

import pathlib

import yaml

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent
DATA: pathlib.Path = ROOT / "data"


def load(name: str) -> list | dict:
    """Parse ``data/<name>.yml`` → list/dict, or ``[]`` when the file is absent."""
    path = DATA / f"{name}.yml"
    if not path.exists():
        return []
    return yaml.safe_load(path.read_text()) or []


def esc(text: object) -> str:
    """Collapse whitespace runs for clean single-line Markdown (no HTML-escaping)."""
    return " ".join(str("" if text is None else text).split())
