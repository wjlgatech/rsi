#!/usr/bin/env python3
"""Schema gate for data/*.yml — every entry needs its required fields + a real URL.

The cheap offline half of `make check` (the CI link-checker/lychee is the online half
that confirms URLs actually resolve). Ported from FM-os; adapted to rsi's data files.
"""
from __future__ import annotations

import sys

from rsidata import DATA, load

REQUIRED = {
    "papers": ["title", "url"],
    "tools": ["name", "url", "category"],
    "people": ["name", "url"],
    "labs": ["name", "url", "category"],
    "benchmarks": ["name", "url"],
    "talks": ["title", "url"],
}


def check_entry(entry: object, fields: list[str], where: str, seen: set) -> list[str]:
    if not isinstance(entry, dict):
        return [f"{where}: entry must be a mapping"]
    errs = [f"{where}: missing required field '{f}'" for f in fields if not entry.get(f)]
    url = str(entry.get("url", ""))
    if url and not url.startswith(("http://", "https://")):
        errs.append(f"{where}: url must be http(s):// — got {url!r}")
    # Identity is (title/name, url): a video page or proceedings URL legitimately hosts
    # several distinct talks/papers, so URL alone isn't a duplicate — the same title AT
    # the same URL is.
    ident = (str(entry.get("title") or entry.get("name") or "").lower(), url)
    if url and ident in seen:
        errs.append(f"{where}: duplicate entry {ident[0]!r} @ {url}")
    if url:
        seen.add(ident)
    return errs


def check_file(name: str, fields: list[str]) -> list[str]:
    if not (DATA / f"{name}.yml").exists():
        return [f"{name}.yml: missing"]
    rows = load(name)
    if not isinstance(rows, list):
        return [f"{name}.yml: top level must be a list"]
    seen: set = set()
    errs: list[str] = []
    for i, entry in enumerate(rows):
        errs += check_entry(entry, fields, f"{name}.yml[{i}]", seen)
    return errs


def main() -> int:
    errors: list[str] = []
    for name, fields in REQUIRED.items():
        errors += check_file(name, fields)
    if errors:
        print("Validation FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1
    total = sum(len(load(n)) for n in REQUIRED)
    print(f"Validation passed — {total} entries across {len(REQUIRED)} data/*.yml files have required fields + URLs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
