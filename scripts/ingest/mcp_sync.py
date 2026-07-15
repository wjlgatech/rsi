#!/usr/bin/env python3
"""mcp_sync.py — the MCP-SERVERS source adapter (unit 3 of the certified registry).

Discovers RSI-relevant Model Context Protocol servers/plugins on GitHub (repos that ship an
`mcp.json`/server manifest, or are tagged `mcp` / "model context protocol") and emits them as
`kind:"mcp"` candidates in the shared schema. MCP is how RSI research agents get tools
(ToolUniverse-style ecosystems), so a certified MCP shelf is squarely on-topic.

Reuses github_sync's rate-limited GET, relevance lexicon, and deny-list (DRY). Signals-only
(🥈) like the other adapters; the deep 🥇 works/safe checks are the certifier's job.

Usage:
  mcp_sync.py --readme README.md --out knowledge/candidates.mcp.json \\
              [--min-stars 20] [--per-query 8] [--confirm-manifest]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse

import github_sync as gh  # same dir — reuse _get, is_rsi_relevant, DENY_SUBSTRINGS, existing_repos

MCP_QUERIES = [
    "MCP server agent tools",
    "model context protocol research",
    "MCP server self-improving agent",
    "MCP tools AI scientist",
    "agentic MCP server automated",
    "model context protocol open-ended",
]

# MCP manifests live at a few conventional paths; presence confirms it's really an MCP server.
_MANIFEST_NAMES = ("mcp.json", ".mcp.json", "server.json")


def _has_manifest(slug: str, token: str | None) -> bool:
    root = gh._get(f"{gh.API}/repos/{slug}/contents", token)
    if not isinstance(root, list):
        return False
    names = {e.get("name", "") for e in root}
    return bool(names & set(_MANIFEST_NAMES)) or "mcp" in {n.lower() for n in names}


def discover(readme: str, token: str | None, min_stars: int, per_query: int,
             confirm: bool) -> list[dict]:
    have = gh.existing_repos(readme)
    seen, out = set(), []
    print(f"MCP: {len(MCP_QUERIES)} queries, min_stars={min_stars}, confirm_manifest={confirm}",
          file=sys.stderr)
    for q in MCP_QUERIES:
        url = (f"{gh.API}/search/repositories?q={urllib.parse.quote(q)}"
               f"&sort=stars&order=desc&per_page={per_query}")
        d = gh._get(url, token)
        if not isinstance(d, dict):
            continue
        for r in d.get("items", []):
            slug = r["full_name"]
            desc = r.get("description") or ""
            if slug in have or slug in seen:
                continue
            if r["stargazers_count"] < min_stars:
                continue
            if any(s in slug.lower() for s in gh.DENY_SUBSTRINGS):
                continue
            # Must be BOTH an MCP thing AND RSI-relevant (mcp alone is a huge generic space).
            is_mcp = "mcp" in slug.lower() or "mcp" in desc.lower() or "model context protocol" in desc.lower()
            if not (is_mcp and gh.is_rsi_relevant(slug, desc)):
                continue
            seen.add(slug)
            has_manifest = _has_manifest(slug, token) if confirm else None
            if confirm and not has_manifest:
                continue
            out.append({
                "domain": "tooling", "kind": "mcp", "id": slug,
                "title": slug, "url": r["html_url"], "score": r["stargazers_count"],
                "action": "add",
                "evidence": {"stars": r["stargazers_count"], "pushed": r["pushed_at"][:10],
                             "desc": desc[:140], "matched": q,
                             **({"has_manifest": has_manifest} if has_manifest is not None else {})},
            })
        time.sleep(1)
    out.sort(key=lambda c: c["score"], reverse=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--out", default="knowledge/candidates.mcp.json")
    ap.add_argument("--min-stars", type=int, default=20)
    ap.add_argument("--per-query", type=int, default=8)
    ap.add_argument("--confirm-manifest", action="store_true",
                    help="verify each repo ships an MCP manifest (extra API calls; best with a token)")
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    print(f"auth: {'GITHUB_TOKEN' if token else 'UNAUTH (60/hr)'}", file=sys.stderr)
    readme = open(args.readme, encoding="utf-8").read()
    cands = discover(readme, token, args.min_stars, args.per_query, args.confirm_manifest)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"source": "mcp", "candidates": cands}, f, indent=2)
    print(f"\n✓ {len(cands)} MCP candidate(s) → {args.out}", file=sys.stderr)
    for c in cands[:10]:
        print(f"  {c['id']}  ⭐{c['score']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
