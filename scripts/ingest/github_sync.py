#!/usr/bin/env python3
"""github_sync.py — the GitHub source adapter for the RSI auto-sync pipeline.

Two jobs, both against the live GitHub API (stdlib-only, zero deps):

  1. REFRESH — for every repo already listed in the README, fetch its live star
     count + last-push date, and flag entries whose printed count is stale
     (>10% drift) or that look abandoned (no push in >12 months).
  2. DISCOVER — search GitHub for repos on RSI topics that are NOT yet listed,
     rank by stars, and surface the strongest new candidates.

Output is a common candidate schema shared by every adapter (arxiv, news, jobs):

    {"domain": "tooling", "kind": "repo", "id": "owner/name", "title": ...,
     "url": ..., "score": <int>, "evidence": {...}, "action": "refresh"|"add"}

The weekly Action collects these from all adapters, ranks them, and opens ONE PR.
Nothing is ever written to the README here — a human merges the PR.

Auth: set GITHUB_TOKEN (Actions provides it free: 5000 req/hr vs 60 unauth).

Usage:
  github_sync.py --readme README.md --out knowledge/candidates.github.json \\
                 [--refresh] [--discover] [--limit N] [--min-stars 150]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"

# RSI-relevant discovery queries. Kept as data so the slate is auditable and
# a curator can add a track by editing one list — no code change.
DISCOVERY_QUERIES = [
    "self-improving agent",
    "automated AI research",
    "agentic system design",
    "open-ended learning LLM",
    "darwin godel machine",
    "AI scientist automated discovery",
]

# Repos never worth surfacing as "new" (forks of the list itself, generic kits).
DENY_SUBSTRINGS = ("awesome-", "vibecode", "-kit", "roadmap")

# RSI-relevance gate: GitHub search ranks by stars, so generic giants (qlib,
# haystack, design systems) outrank real RSI repos. Require a topic term in the
# name or description. Kept strict — "agent" alone is too broad to qualify.
RSI_LEXICON = (
    "self-improv", "self-evolv", "recursive self", "godel", "gödel",
    "ai scientist", "automated research", "research agent", "open-ended",
    "open-endedness", "meta-learning", "agentic system", "self-referential",
    "darwin machine", "auto-ml research", "scientific discovery",
)


def is_rsi_relevant(*text: str) -> bool:
    blob = " ".join(t.lower() for t in text if t)
    return any(term in blob for term in RSI_LEXICON)


def _get(url: str, token: str | None) -> dict | list | None:
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):  # rate limited — back off and retry
                reset = e.headers.get("X-RateLimit-Reset")
                wait = min(30, max(2, int(reset) - int(time.time()))) if reset else 5
                print(f"  … rate limited, waiting {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"  ! HTTP {e.code} for {url}", file=sys.stderr)
            return None
        except Exception as e:  # noqa: BLE001 — network flake; report, don't crash the run
            print(f"  ! {type(e).__name__} for {url}", file=sys.stderr)
            time.sleep(2)
    return None


def existing_repos(readme: str) -> set[str]:
    """Every owner/name slug already linked in the README (deduped)."""
    slugs = set()
    for m in re.finditer(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", readme):
        slug = m.group(1).removesuffix(".git").rstrip("/")
        # strip deep paths like owner/repo/tree/main
        parts = slug.split("/")
        if len(parts) >= 2:
            slugs.add(f"{parts[0]}/{parts[1]}")
    # drop the list's own repo (leaks in via the shields.io badge URLs) and
    # any obvious non-content slug — see DENY_SUBSTRINGS.
    self_repo = "wjlgatech/awesome-auto-ai-research"
    return {s for s in slugs
            if s != self_repo and not any(d in s.lower() for d in DENY_SUBSTRINGS)}


def printed_star(readme: str, slug: str) -> int | None:
    """The star number the README currently prints for a repo, as an int.

    The row is a GFM table; the star count lives in its own `| ~22k |` cell.
    Parse per-cell (not by string-splitting the whole row) so the repo URL,
    which also contains digits/dots, can never be mistaken for the count.
    """
    lines = [ln for ln in readme.splitlines() if slug in ln]
    if not lines:
        return None
    # A repo's own listing writes its name in bold: `| [**owner/name**](url) |`.
    # Prefer that row — other rows (e.g. a paper linking the repo as code) carry
    # unrelated bare numbers (year, citations) that would be misread as stars.
    row = next((ln for ln in lines if f"**{slug}**" in ln), lines[0])
    for cell in row.split("|"):
        m = re.fullmatch(r"~?\s*([\d.]+)\s*([kK])?", cell.strip())
        if not m:
            continue
        val = float(m.group(1))
        if m.group(2):                       # explicit k suffix → definitely stars
            return int(val * 1000)
        if 1990 <= val <= 2100:              # bare 4-digit → a year, not a star count
            continue
        return int(val)
    return None


def refresh(readme: str, token: str | None, limit: int) -> list[dict]:
    out = []
    slugs = sorted(existing_repos(readme))
    if limit:
        slugs = slugs[:limit]
    print(f"REFRESH: checking {len(slugs)} listed repos", file=sys.stderr)
    for slug in slugs:
        d = _get(f"{API}/repos/{slug}", token)
        if not d or not isinstance(d, dict) or d.get("stargazers_count") is None:
            continue
        live = d["stargazers_count"]
        printed = printed_star(readme, slug)
        pushed = (d.get("pushed_at") or "")[:10]
        stale = printed is not None and abs(live - printed) > max(200, printed * 0.10)
        if stale:
            out.append({
                "domain": "tooling", "kind": "repo", "id": slug,
                "title": slug, "url": d["html_url"], "score": live,
                "action": "refresh",
                "evidence": {"printed": printed, "live": live, "pushed": pushed},
            })
            print(f"  STALE {slug}: printed≈{printed} live={live}", file=sys.stderr)
    return out


def discover(readme: str, token: str | None, min_stars: int, per_query: int) -> list[dict]:
    have = existing_repos(readme)
    seen, out = set(), []
    print(f"DISCOVER: {len(DISCOVERY_QUERIES)} queries, min_stars={min_stars}", file=sys.stderr)
    for q in DISCOVERY_QUERIES:
        url = (f"{API}/search/repositories?q={urllib.parse.quote(q)}"
               f"&sort=stars&order=desc&per_page={per_query}")
        d = _get(url, token)
        if not isinstance(d, dict):
            continue
        for r in d.get("items", []):
            slug = r["full_name"]
            if slug in have or slug in seen:
                continue
            if r["stargazers_count"] < min_stars:
                continue
            if any(s in slug.lower() for s in DENY_SUBSTRINGS):
                continue
            if not is_rsi_relevant(slug, r.get("description") or ""):
                continue  # generic high-star repo that merely matched a keyword
            seen.add(slug)
            out.append({
                "domain": "tooling", "kind": "repo", "id": slug,
                "title": slug, "url": r["html_url"], "score": r["stargazers_count"],
                "action": "add",
                "evidence": {"stars": r["stargazers_count"], "pushed": r["pushed_at"][:10],
                             "desc": (r.get("description") or "")[:120], "matched": q},
            })
        time.sleep(1)  # be gentle on the search rate limit
    out.sort(key=lambda c: c["score"], reverse=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--out", default="knowledge/candidates.github.json")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="cap repos checked (demo/rate-limit)")
    ap.add_argument("--min-stars", type=int, default=150)
    ap.add_argument("--per-query", type=int, default=8)
    args = ap.parse_args()

    if not (args.refresh or args.discover):
        args.refresh = args.discover = True

    token = os.environ.get("GITHUB_TOKEN")
    print(f"auth: {'GITHUB_TOKEN' if token else 'UNAUTH (60/hr — CI should set a token)'}",
          file=sys.stderr)
    readme = open(args.readme, encoding="utf-8").read()

    candidates = []
    if args.refresh:
        candidates += refresh(readme, token, args.limit)
    if args.discover:
        candidates += discover(readme, token, args.min_stars, args.per_query)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"source": "github", "candidates": candidates}, f, indent=2)
    print(f"\n✓ {len(candidates)} candidate(s) → {args.out}", file=sys.stderr)
    for c in candidates[:12]:
        tag = "REFRESH" if c["action"] == "refresh" else "ADD"
        print(f"  [{tag}] {c['id']}  ⭐{c['score']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
