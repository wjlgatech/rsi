#!/usr/bin/env python3
"""workflows_sync.py — the WORKFLOWS source adapter (unit 4 of the certified registry).

Discovers RSI-relevant multi-step agent workflows / orchestration pipelines on GitHub
(LangGraph graphs, agent pipelines, self-improvement loops shipped as reusable workflows)
and emits them as `kind:"workflow"` candidates. Workflows are the least-standardized unit —
there's no single manifest file — so discovery leans on topic/description signals, and the
relevance gate is doubled (must read as BOTH a workflow AND RSI) to fight noise.

Reuses github_sync helpers (DRY). Signals-only (🥈); 🥇 works/safe is the certifier's job.

Usage:
  workflows_sync.py --readme README.md --out knowledge/candidates.workflows.json \\
                    [--min-stars 30] [--per-query 8]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse

import github_sync as gh

WORKFLOW_QUERIES = [
    "agent workflow self-improving",
    "agentic pipeline automated research",
    "LangGraph self-improvement workflow",
    "multi-agent orchestration open-ended",
    "self-improving agent loop workflow",
    "automated research pipeline agent",
]

# A repo reads as a "workflow" if it says so — no standard manifest exists for this unit.
_WORKFLOW_HINTS = ("workflow", "pipeline", "orchestrat", "langgraph", "loop", "graph of agents",
                   "multi-agent", "multi agent", "dag")


def _is_workflow(slug: str, desc: str) -> bool:
    blob = f"{slug} {desc}".lower()
    return any(h in blob for h in _WORKFLOW_HINTS)


def discover(readme: str, token: str | None, min_stars: int, per_query: int) -> list[dict]:
    have = gh.existing_repos(readme)
    seen, out = set(), []
    print(f"WORKFLOWS: {len(WORKFLOW_QUERIES)} queries, min_stars={min_stars}", file=sys.stderr)
    for q in WORKFLOW_QUERIES:
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
            # Doubled gate: must read as a workflow AND be RSI-relevant.
            if not (_is_workflow(slug, desc) and gh.is_rsi_relevant(slug, desc)):
                continue
            seen.add(slug)
            out.append({
                "domain": "tooling", "kind": "workflow", "id": slug,
                "title": slug, "url": r["html_url"], "score": r["stargazers_count"],
                "action": "add",
                "evidence": {"stars": r["stargazers_count"], "pushed": r["pushed_at"][:10],
                             "desc": desc[:140], "matched": q},
            })
        time.sleep(1)
    out.sort(key=lambda c: c["score"], reverse=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--out", default="knowledge/candidates.workflows.json")
    ap.add_argument("--min-stars", type=int, default=30)
    ap.add_argument("--per-query", type=int, default=8)
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    print(f"auth: {'GITHUB_TOKEN' if token else 'UNAUTH (60/hr)'}", file=sys.stderr)
    readme = open(args.readme, encoding="utf-8").read()
    cands = discover(readme, token, args.min_stars, args.per_query)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"source": "workflows", "candidates": cands}, f, indent=2)
    print(f"\n✓ {len(cands)} workflow candidate(s) → {args.out}", file=sys.stderr)
    for c in cands[:10]:
        print(f"  {c['id']}  ⭐{c['score']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
