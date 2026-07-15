#!/usr/bin/env python3
"""skills_sync.py — the AGENT-SKILLS source adapter (unit 1 of the certified registry).

skills.sh lists agent skills ranked by install count. This discovers RSI-relevant agent
skills on GitHub (repos that ship a SKILL.md / a skills/ dir — the Claude Code / Cursor /
Codex skill format) and emits them as `kind:"skill"` candidates in the shared schema, so the
same weekly PR + certifier that handle repos handle skills with zero new plumbing.

Signals-only by design (the 🥈 Verified tier): discover + relevance-gate + best-effort
SKILL.md confirmation. The deep 🥇 checks (works/safe) are the certifier's job, later.

Reuses github_sync's rate-limited GET, relevance lexicon, and deny-list (DRY — one source).

Usage:
  skills_sync.py --readme README.md --out knowledge/candidates.skills.json \\
                 [--min-stars 20] [--per-query 8] [--confirm-skill-md]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse

import github_sync as gh  # same dir — reuse _get, is_rsi_relevant, DENY_SUBSTRINGS, existing_repos

# Skill-flavored discovery queries × RSI topics. Data, not code.
SKILL_QUERIES = [
    "agent skill self-improving",
    "claude code skill agent",
    "SKILL.md agent",
    "self-improving skill AI agent",
    "agentic workflow skill",
    "MCP skill research agent",
]


def _has_skill_md(slug: str, token: str | None) -> bool:
    """Best-effort: does the repo actually ship a SKILL.md (root or a skills/ dir)?"""
    root = gh._get(f"{gh.API}/repos/{slug}/contents", token)
    if not isinstance(root, list):
        return False
    names = {e.get("name", "") for e in root}
    if "SKILL.md" in names:
        return True
    if "skills" in names:  # skills live under a skills/ dir (the anthropics/skills layout)
        sub = gh._get(f"{gh.API}/repos/{slug}/contents/skills", token)
        if isinstance(sub, list):
            # a skills dir whose children are dirs (each a skill) or contain SKILL.md
            return any(e.get("type") == "dir" or e.get("name") == "SKILL.md" for e in sub)
    return False


def discover(readme: str, token: str | None, min_stars: int, per_query: int,
             confirm: bool) -> list[dict]:
    have = gh.existing_repos(readme)          # never re-list something already curated
    seen, out = set(), []
    print(f"SKILLS: {len(SKILL_QUERIES)} queries, min_stars={min_stars}, confirm_skill_md={confirm}",
          file=sys.stderr)
    for q in SKILL_QUERIES:
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
            if not gh.is_rsi_relevant(slug, desc):
                continue
            seen.add(slug)
            has_md = _has_skill_md(slug, token) if confirm else None
            if confirm and not has_md:
                continue  # asked to confirm and it has no SKILL.md → not really a skill
            out.append({
                "domain": "tooling", "kind": "skill", "id": slug,
                "title": slug, "url": r["html_url"], "score": r["stargazers_count"],
                "action": "add",
                "evidence": {"stars": r["stargazers_count"], "pushed": r["pushed_at"][:10],
                             "desc": desc[:140], "matched": q,
                             **({"has_skill_md": has_md} if has_md is not None else {})},
            })
        time.sleep(1)
    out.sort(key=lambda c: c["score"], reverse=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--out", default="knowledge/candidates.skills.json")
    ap.add_argument("--min-stars", type=int, default=20)
    ap.add_argument("--per-query", type=int, default=8)
    ap.add_argument("--confirm-skill-md", action="store_true",
                    help="verify each repo ships a SKILL.md (extra API calls; best with a token)")
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    print(f"auth: {'GITHUB_TOKEN' if token else 'UNAUTH (60/hr)'}", file=sys.stderr)
    readme = open(args.readme, encoding="utf-8").read()
    cands = discover(readme, token, args.min_stars, args.per_query, args.confirm_skill_md)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"source": "skills", "candidates": cands}, f, indent=2)
    print(f"\n✓ {len(cands)} skill candidate(s) → {args.out}", file=sys.stderr)
    for c in cands[:10]:
        md = c["evidence"].get("has_skill_md")
        print(f"  {c['id']}  ⭐{c['score']}{'  ✓SKILL.md' if md else ''}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
