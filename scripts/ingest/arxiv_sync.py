#!/usr/bin/env python3
"""arxiv_sync.py — the arXiv (knowledge) source adapter for the RSI pipeline.

Queries arXiv's Atom API for recent papers on RSI topics AND by the tracked
Recursive co-founders, drops anything already linked in the README, and emits
candidates in the shared schema (see github_sync.py).

Recency-weighted score so this week's papers float to the top of the weekly PR:
    score = base(200) − days_old, floored at 0. A citation signal can be layered
    in later via Semantic Scholar; arXiv alone has none, and no-evidence ⇒ we
    don't invent one.

Usage:
  arxiv_sync.py --readme README.md --out knowledge/candidates.arxiv.json \\
                [--days 14] [--max-per-query 12]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API = "http://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}

# Topic queries — data, not code, so a curator adds a track with one line.
TOPIC_QUERIES = [
    'abs:"self-improving"',
    'abs:"recursive self-improvement"',
    'abs:"automated AI research" OR abs:"AI scientist"',
    'abs:"open-endedness" OR abs:"open-ended learning"',
    'abs:"agentic system" AND abs:"design"',
    'abs:"meta-learning" AND abs:"self-improvement"',
]
# The 8 Recursive co-founders — follow the people, not just the keywords.
AUTHOR_QUERIES = [
    'au:"Jeff Clune"', 'au:"Tim Rocktaschel"', 'au:"Yuandong Tian"',
    'au:"Mingchen Zhuge"', 'au:"Yingbo Zhou"',
]


def _fetch(query: str, max_results: int) -> str | None:
    params = urllib.parse.urlencode({
        "search_query": query, "sortBy": "submittedDate",
        "sortOrder": "descending", "max_results": max_results,
    })
    url = f"{API}?{params}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                body = r.read().decode("utf-8", "replace")
            if body.strip():
                return body
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"  ! {type(e).__name__} ({query[:30]}…) attempt {attempt+1}", file=sys.stderr)
        time.sleep(3 * (attempt + 1))  # arXiv is slow/rate-touchy — real backoff
    return None


def existing_arxiv_ids(readme: str) -> set[str]:
    """arXiv IDs already linked (abs/ or pdf/), normalized without version."""
    ids = set()
    for m in re.finditer(r"arxiv\.org/(?:abs|pdf)/([\d.]+|[a-z\-]+/\d+)", readme):
        ids.add(m.group(1).removesuffix(".").split("v")[0])
    return ids


def _entry_to_candidate(e: ET.Element, today: dt.date) -> dict | None:
    link = e.find("a:id", NS)
    title = e.find("a:title", NS)
    pub = e.find("a:published", NS)
    if link is None or title is None or pub is None:
        return None
    arxiv_id = link.text.strip().split("/abs/")[-1].split("v")[0]
    published = pub.text[:10]
    try:
        days_old = (today - dt.date.fromisoformat(published)).days
    except ValueError:
        days_old = 999
    authors = [a.findtext("a:name", default="", namespaces=NS)
               for a in e.findall("a:author", NS)][:6]
    summary = (e.findtext("a:summary", default="", namespaces=NS) or "").strip()
    return {
        "domain": "knowledge", "kind": "paper", "id": arxiv_id,
        "title": re.sub(r"\s+", " ", title.text).strip(),
        "url": f"https://arxiv.org/abs/{arxiv_id}",
        "score": max(0, 200 - days_old), "action": "add",
        "evidence": {"published": published, "days_old": days_old,
                     "authors": authors, "summary": summary[:200]},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--out", default="knowledge/candidates.arxiv.json")
    ap.add_argument("--days", type=int, default=21, help="only keep papers this fresh")
    ap.add_argument("--max-per-query", type=int, default=12)
    ap.add_argument("--today", help="ISO date override for deterministic CI (defaults to run date)")
    args = ap.parse_args()

    # Date.now is unavailable in some sandboxes; allow an explicit override, else
    # read it from the OS clock here (real CLI run, not a workflow-script sandbox).
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()

    readme = open(args.readme, encoding="utf-8").read()
    have = existing_arxiv_ids(readme)
    print(f"arxiv: {len(have)} papers already listed; window={args.days}d", file=sys.stderr)

    seen, candidates = set(), []
    for q in TOPIC_QUERIES + AUTHOR_QUERIES:
        body = _fetch(q, args.max_per_query)
        if not body:
            continue
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            print(f"  ! unparseable response for {q[:30]}…", file=sys.stderr)
            continue
        for e in root.findall("a:entry", NS):
            c = _entry_to_candidate(e, today)
            if not c:
                continue
            if c["id"] in have or c["id"] in seen:
                continue
            if c["evidence"]["days_old"] > args.days:
                continue
            seen.add(c["id"])
            candidates.append(c)
        time.sleep(3)  # arXiv asks for ~3s between calls

    candidates.sort(key=lambda c: c["score"], reverse=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"source": "arxiv", "candidates": candidates}, f, indent=2)
    print(f"\n✓ {len(candidates)} new paper(s) → {args.out}", file=sys.stderr)
    for c in candidates[:10]:
        print(f"  {c['evidence']['published']}  {c['title'][:62]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
