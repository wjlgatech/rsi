#!/usr/bin/env python3
"""One-time bootstrap: knowledge/graph.json → data/*.yml (spec-as-data).

rsi's graph already parsed every entry from the old hand-maintained README, so we
seed the new data files from it (lossless) instead of retyping. After this runs,
data/*.yml is the source of truth and scripts/build_readme.py regenerates the README.
Idempotent-ish: overwrites the entry files; never touches meta.yml (hand-authored).

Usage:  python3 scripts/graph_to_data.py
"""
from __future__ import annotations

import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
GRAPH = json.loads((ROOT / "knowledge" / "graph.json").read_text())
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

NODES = GRAPH["nodes"]
url1 = lambda n: (n.get("links") or [""])[0]
by_type = lambda t: [n for n in NODES if n["type"] == t]


def dump(name: str, rows: list[dict], header: str) -> None:
    body = yaml.safe_dump(rows, sort_keys=False, allow_unicode=True, width=100, default_flow_style=False)
    (DATA / f"{name}.yml").write_text(f"# {header}\n# Generated once from knowledge/graph.json; now edit here (README is generated).\n{body}")
    print(f"  data/{name}.yml — {len(rows)} entries")


def clean(d: dict) -> dict:
    """Drop empty values so the YAML stays terse and validate stays meaningful."""
    return {k: v for k, v in d.items() if v not in (None, "", [], 0)}


def has_url(rows: list[dict]) -> list[dict]:
    """Drop entries without a URL — a linkable resource needs one; meta-notes don't belong."""
    return [r for r in rows if r.get("url")]


# Recover the Code column: has_code edges (paper→repo) → the repo's URL, so the
# generated paper table re-creates the exact same has_code edges awesome_kg extracts.
_id_url = {n["id"]: url1(n) for n in NODES}
_code = {e["src"]: _id_url.get(e["dst"], "") for e in GRAPH["edges"] if e["type"] == "has_code"}
_id_name = {n["id"]: n["name"] for n in NODES}
_code_by_title = {_id_name[src]: url for src, url in _code.items() if src in _id_name}

papers = [clean({
    "title": n["name"], "url": url1(n), "authors": n.get("authors"), "year": n.get("year"),
    "venue": n.get("venue"), "citations": n.get("citations"), "group": n.get("category"),
    "code": _code_by_title.get(n["name"], ""), "blurb": n.get("summary", ""),
}) for n in by_type("paper")]

tools = [clean({
    "name": n["name"], "url": url1(n), "category": n.get("category"),
    "blurb": n.get("summary", ""), "stars": n.get("stars"), "status": n.get("status"),
}) for n in by_type("repo")]

people = [clean({
    "name": n["name"], "url": url1(n), "category": n.get("category"),
    "focus": n.get("summary", ""), "links": n.get("links", []),
}) for n in by_type("person")]

labs = [clean({
    "name": n["name"], "url": url1(n), "category": n.get("category"),
    "focus": n.get("summary", ""),
}) for n in by_type("lab")]

benchmarks = [clean({
    "name": n["name"], "url": url1(n), "category": n.get("category"),
    "blurb": n.get("summary", ""), "venue": n.get("venue"), "year": n.get("year"),
    "citations": n.get("citations"),
}) for n in by_type("benchmark")]

talks = [clean({
    "title": n["name"], "url": url1(n), "speaker": n.get("authors"),
    "venue": n.get("venue"), "year": n.get("year"), "group": n.get("category"),
}) for n in by_type("talk")]

print("bootstrapping data/*.yml from knowledge/graph.json:")
dump("papers", has_url(papers), "Papers — group = subfield taxonomy")
dump("tools", has_url(tools), "Open-source tools & repos — category = stack")
dump("people", has_url(people), "People to follow — category = role")
dump("labs", has_url(labs), "Labs & orgs — category = kind")
dump("benchmarks", has_url(benchmarks), "Benchmarks & leaderboards")
dump("talks", has_url(talks), "Talks, interviews & podcasts")
print("done. Next: hand-author data/meta.yml, then `make build`.")
