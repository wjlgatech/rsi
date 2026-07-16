#!/usr/bin/env python3
"""Render README.md from data/*.yml + data/prose/*.md — the single source of truth.

The README is a BUILD ARTIFACT. Never hand-edit it; edit data/ and run `make build`
(CI drift-gates the two via `--check`). Ported from FM-os, adapted to rsi.

Design note — the graph coupling: rsi's README tables are parsed by awesome_kg.py into
knowledge/graph.json (the web app + "Ask the field" read it). So the two entry sections
we GENERATE (Papers, Tools) emit the exact table shape + category H3s awesome_kg expects,
and every other section (People, Talks, Benchmarks, narrative prose) is inlined VERBATIM
from data/prose/*.md — so `data → build_readme → README → awesome_kg → graph` reproduces
the same nodes/edges. Verify with: python3 scripts/build_readme.py && python3 scripts/awesome_kg.py build README.md ...
"""
from __future__ import annotations

import json
import sys

from rsidata import DATA, ROOT, esc, load

README = ROOT / "README.md"
CERTS = ROOT / "knowledge" / "certifications.json"


def prose(name: str) -> str:
    """Inline a verbatim prose block (raises if missing — a silent drop is worse)."""
    return (DATA / "prose" / f"{name}.md").read_text().rstrip()


def _stars(n: int) -> str:
    """Render a star count the way the list always has: ~48k, ~1.2k, ~150."""
    return f"~{n/1000:g}k" if n >= 1000 else f"~{n}"


def _grouped(entries: list, key: str) -> list[tuple[str, list]]:
    """Group entries by a field, preserving first-appearance order (== README order)."""
    order: list[str] = []
    buckets: dict[str, list] = {}
    for e in entries:
        g = e.get(key) or "More"
        if g not in buckets:
            buckets[g] = []
            order.append(g)
        buckets[g].append(e)
    return [(g, buckets[g]) for g in order]


def fmt_paper(e: dict) -> str:
    cit = f"~{e['citations']}" if e.get("citations") else "—"
    code = f"[💻]({e['code']})" if e.get("code") else "—"
    return (f"| [**{esc(e['title'])}**]({e['url']}) | {esc(e.get('authors',''))} "
            f"| {esc(e.get('venue',''))} | {esc(e.get('year',''))} | {cit} | {code} |")


def fmt_tool(e: dict) -> str:
    stars = _stars(e["stars"]) if isinstance(e.get("stars"), int) else "🆕"
    return (f"| [**{esc(e['name'])}**]({e['url']}) | {esc(e.get('blurb',''))} "
            f"| {stars} | {esc(e.get('status',''))} |")


def fmt_benchmark(e: dict) -> str:
    cit = f"~{e['citations']}" if e.get("citations") else "—"
    return (f"| [**{esc(e['name'])}**]({e['url']}) | {esc(e.get('blurb',''))} "
            f"| {esc(e.get('venue',''))} | {esc(e.get('year',''))} | {cit} |")


PAPER_HEAD = ["| Paper | Authors | Venue | Year | Citations | Code |",
              "|-------|---------|-------|------|-----------|------|"]
TOOL_HEAD = ["| Repo | Description | Stars | Status |",
             "|------|-------------|-------|--------|"]
BENCH_HEAD = ["| Benchmark | Focus | Venue | Year | Citations |",
              "|-----------|-------|-------|------|-----------|"]


def gen_section(h2: str, note: str, entries: list, group_key: str, head: list[str], fmt) -> str:
    out = [h2, ""]
    if note:
        out += [note, ""]
    for group, rows in _grouped(entries, group_key):
        out += [f"### {group}", "", *head, *[fmt(e) for e in rows], ""]
    return "\n".join(out).rstrip()


def gen_certified() -> str:
    """The 🏅 Certified Tooling summary — counts + link, from certifications.json.
    Dateless on purpose: a date would drift the README daily against the gate."""
    if not CERTS.exists():
        return ""
    certs = json.loads(CERTS.read_text()).get("certifications", [])
    from collections import Counter
    d = Counter(c["tier"] for c in certs)
    return "\n".join([
        "## 🏅 Certified Tooling",
        "",
        "Tools here earn an **evidence-backed** tier, not an install count — the trust layer "
        "[skills.sh](https://www.skills.sh/) lacks. "
        f"**{d.get('🥇 RSI-Certified',0)} 🥇 Certified · {d.get('🥈 Verified',0)} 🥈 Verified · "
        f"{d.get('🥉 Listed',0)} 🥉 Listed.**",
        "",
        "🥈 Verified = relevant + maintained (machine-checked). 🥇 adds *works* + *safe* via "
        "`anyagent analyze`/`brace`; no-evidence ⇒ no badge. "
        "→ **[Full certified list](docs/CERTIFIED.md)** · [raw data](knowledge/certifications.json)",
    ])


def footer() -> str:
    return ("<sub>README generated from <code>data/*.yml</code> + <code>data/prose/*.md</code> "
            "by <code>scripts/build_readme.py</code> — do not edit by hand; run <code>make build</code>.</sub>")


def build() -> str:
    meta = load("meta")
    notes = meta.get("notes", {})
    blocks = [
        prose("_header"),
        esc(meta["applied_banner"]),
        prose("_toc"),
        prose("knowledge-graph"),
        prose("taxonomy"),
        gen_section("## 📄 Papers", notes.get("papers", ""), load("papers"), "group", PAPER_HEAD, fmt_paper),
        gen_section("## 🛠️ Open-Source Tools & Repos", notes.get("tools", ""), load("tools"), "category", TOOL_HEAD, fmt_tool),
        gen_certified(),
        prose("people"),
        prose("talks"),
        gen_section("## 📈 Benchmarks & Leaderboards", "", load("benchmarks"), "category", BENCH_HEAD, fmt_benchmark),
        prose("timeline"),
        prose("roadmaps"),
        prose("competitive"),
        prose("contribute"),
        prose("citation"),
        footer(),
    ]
    return "\n\n---\n\n".join(b for b in blocks if b) + "\n"


def main() -> int:
    text = build()
    if "--check" in sys.argv:
        current = README.read_text() if README.exists() else ""
        if current != text:
            print("README.md is out of date vs data/*.yml. Run `make build` and commit.", file=sys.stderr)
            return 1
        print("README.md is up to date with data/*.yml.")
        return 0
    README.write_text(text)
    print(f"Wrote {README.relative_to(ROOT)} ({len(text.splitlines())} lines).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
