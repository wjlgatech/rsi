#!/usr/bin/env python3
"""check_ingest.py — the finish line for the auto-sync pipeline.

`anyagent goal` flagged that this repo had no verifiable definition of "done" for
ingestion. This is it: a deterministic gate (stdlib-only, exits non-zero on any
failure so CI blocks a bad PR). It enforces the honesty rules —

  • every candidate carries the required fields + real evidence (no-evidence ⇒ fail)
  • every URL is well-formed http(s)
  • no `add` candidate duplicates something already in the README (no dupes)
  • refresh candidates actually show a printed→live delta
  • the README still compiles to a >100-node graph (the list didn't collapse)

A missing candidates file is "not measured", not a failure — the graph check
still runs so `make check` is a valid finish line even with nothing to ingest.

Usage:
  check_ingest.py --readme README.md --candidates knowledge/candidates.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

REQUIRED = ("domain", "kind", "id", "url", "score", "action", "evidence")


def check_candidates(readme_text: str, cand_path: str) -> list[str]:
    errs: list[str] = []
    if not os.path.exists(cand_path):
        print(f"  (no {cand_path} — nothing to ingest, not a failure)", file=sys.stderr)
        return errs
    try:
        with open(cand_path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return [f"candidates file unreadable: {e}"]

    cands = data.get("candidates", [])
    existing_urls = set(re.findall(r"https?://[^\s)\"']+", readme_text))
    seen_ids = set()

    for i, c in enumerate(cands):
        tag = f"candidate[{i}] {c.get('id', '?')}"
        for f in REQUIRED:
            if f not in c or c[f] in (None, "", {}):
                errs.append(f"{tag}: missing/empty '{f}'  (no-evidence ⇒ reject)")
        u = c.get("url", "")
        if not isinstance(u, str) or not u.startswith(("http://", "https://")):
            errs.append(f"{tag}: url not http(s): {c.get('url')!r}")
        key = (c.get("kind"), c.get("id"))
        if key in seen_ids:
            errs.append(f"{tag}: duplicate within candidates")
        seen_ids.add(key)

        if c.get("action") == "add" and c.get("url") in existing_urls:
            errs.append(f"{tag}: 'add' duplicates a URL already in README")
        if c.get("action") == "refresh":
            ev = c.get("evidence", {})
            if "printed" not in ev or "live" not in ev:
                errs.append(f"{tag}: refresh without printed/live evidence")
            elif ev["printed"] == ev["live"]:
                errs.append(f"{tag}: refresh with zero delta (not stale)")
    print(f"  checked {len(cands)} candidate(s)", file=sys.stderr)
    return errs


def check_graph_compiles(readme_path: str) -> list[str]:
    """The README must still parse into a non-collapsed graph."""
    kg = os.path.join(os.path.dirname(__file__), "awesome_kg.py")
    enrich = os.path.join(os.path.dirname(readme_path) or ".", "knowledge", "enrichments.json")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        out = tf.name
    cmd = [sys.executable, kg, "build", readme_path, "--out", out]
    if os.path.exists(enrich):
        cmd += ["--enrich", enrich]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return [f"graph build failed: {r.stderr.strip()[:200]}"]
    stats = json.load(open(out)).get("stats", {})
    os.unlink(out)
    if stats.get("nodes", 0) <= 100:
        return [f"graph collapsed to {stats.get('nodes')} nodes (expected >100)"]
    print(f"  graph OK: {stats.get('nodes')} nodes · {stats.get('edges')} edges", file=sys.stderr)
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--candidates", default="knowledge/candidates.json")
    args = ap.parse_args()

    readme_text = open(args.readme, encoding="utf-8").read()
    errs = check_candidates(readme_text, args.candidates)
    errs += check_graph_compiles(args.readme)

    if errs:
        print(f"\n✗ ingest check FAILED ({len(errs)} problem(s)):", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("\n✓ ingest check passed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
