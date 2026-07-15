#!/usr/bin/env python3
"""groundbreakers.py — merge adapter candidates → weekly PR body + slate.

Reads every knowledge/candidates.*.json (one per source adapter), dedupes into a
single accumulator, then renders TWO things a human merges in one PR:

  1. 🏆 RSI Groundbreakers — a fixed 5-slot weekly slate, each slot machine-ranked
     from the candidates with its evidence. A slot with no qualifying candidate
     prints "No award this week" — no-evidence ⇒ no award (we never invent one).
  2. Maintenance — stale star refreshes + new-tooling / new-paper tables.

Nothing here edits the README; it writes a PR body the create-pull-request action
attaches, plus the merged knowledge/candidates.json for auditing.

Usage:
  groundbreakers.py --glob "knowledge/candidates.*.json" \\
                    --week 2026-W29 --pr-body /tmp/pr_body.md \\
                    --out knowledge/candidates.json
"""
from __future__ import annotations

import argparse
import glob as globmod
import json
import sys

# Tracked Recursive co-founders — a paper by one of them breaks ties for the
# seminal slot, but does NOT override topic relevance (a co-founder's off-topic
# paper must not win "Seminal RSI Research").
TRACKED_AUTHORS = {
    "jeff clune", "tim rocktaschel", "tim rocktäschel", "richard socher",
    "caiming xiong", "yuandong tian", "tim shi", "mingchen zhuge", "yingbo zhou",
}

# Same relevance gate the github adapter uses — a candidate must be on-topic to
# win the seminal slot, not merely fresh or co-founder-authored.
RSI_LEXICON = (
    "self-improv", "self-evolv", "recursive self", "godel", "gödel",
    "ai scientist", "automated research", "research agent", "open-ended",
    "open-endedness", "meta-learning", "agentic system", "self-referential",
    "scientific discovery", "autonomous", "curriculum", "reward design",
)


def _rsi_relevant(paper: dict) -> bool:
    ev = paper.get("evidence", {})
    blob = f"{paper.get('title','')} {ev.get('summary','')}".lower()
    return any(term in blob for term in RSI_LEXICON)


def load_candidates(pattern: str) -> list[dict]:
    seen, out = set(), []
    for path in sorted(globmod.glob(pattern)):
        if path.endswith("candidates.json"):       # skip our own merged output
            continue
        try:
            data = json.load(open(path, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"  ! skip {path}: {e}", file=sys.stderr)
            continue
        for c in data.get("candidates", []):
            key = (c.get("kind"), c.get("id"))     # dedupe across sources
            if key in seen:
                continue
            seen.add(key)
            out.append(c)
    return out


def _by_author_bonus(paper: dict) -> int:
    authors = {a.lower() for a in paper.get("evidence", {}).get("authors", [])}
    return 30 if authors & TRACKED_AUTHORS else 0  # tie-breaker, not an override


def pick_slate(cands: list[dict]) -> dict:
    """The 5 award slots. Each value is a candidate dict or None (no award)."""
    papers = [c for c in cands if c["kind"] == "paper" and c["action"] == "add"]
    repos_new = [c for c in cands if c["kind"] == "repo" and c["action"] == "add"]
    repos_refresh = [c for c in cands if c["kind"] == "repo" and c["action"] == "refresh"]

    # 🔬 Seminal: freshest *on-topic* paper; a co-founder only breaks a tie.
    seminal_pool = [c for c in papers if _rsi_relevant(c)]
    seminal = max(seminal_pool, key=lambda c: c["score"] + _by_author_bonus(c), default=None)

    # 🚀 Industrial impact: biggest *momentum* — a new high-star repo, or the
    # largest positive star jump among refreshes (velocity, not absolute size).
    def velocity(c):
        ev = c.get("evidence", {})
        return ev.get("live", 0) - ev.get("printed", 0)
    impact_pool = repos_new + [c for c in repos_refresh if velocity(c) > 0]
    impact = max(impact_pool,
                 key=lambda c: velocity(c) if c["action"] == "refresh" else c["score"],
                 default=None)

    # 🌍 Social good / 🎓 best explainer need the news adapter's evidence; until it
    # runs they are honestly empty rather than a forced pick.
    social = next((c for c in cands if c.get("domain") == "social-good"), None)
    explainer = next((c for c in cands if c.get("domain") == "education"), None)

    return {"seminal": seminal, "impact": impact, "social": social,
            "explainer": explainer, "meme": None}  # meme = curator's manual pick


def _award_row(emoji: str, name: str, c: dict | None, note: str) -> str:
    if not c:
        return f"| {emoji} **{name}** | _No award this week_ | — |"
    ev = c.get("evidence", {})
    detail = ""
    if c["kind"] == "paper":
        detail = f"{ev.get('published','')} · {', '.join(ev.get('authors', [])[:2])}"
    elif c["action"] == "refresh":
        detail = f"⭐ {ev.get('printed')}→{ev.get('live')} (+{ev.get('live',0)-ev.get('printed',0)})"
    else:
        detail = f"⭐ {ev.get('stars', c.get('score'))} · new"
    return f"| {emoji} **{name}** | [{c['title']}]({c['url']}) | {detail} |"


def render_pr_body(week: str, cands: list[dict], slate: dict) -> str:
    L = [f"## 🏆 RSI Groundbreakers — {week}", "",
         "_Machine-ranked candidates with evidence. Edit picks, then merge — the "
         "graph recompiles on merge and each award becomes a node._", "",
         "| Slot | Winner | Evidence |", "|------|--------|----------|",
         _award_row("🔬", "Seminal Research", slate["seminal"], ""),
         _award_row("🚀", "Industrial Impact", slate["impact"], ""),
         _award_row("🌍", "Social Good", slate["social"], ""),
         _award_row("🎓", "Best Explainer", slate["explainer"], ""),
         "| 🤯 **Golden Meme** | _curator's pick — most surprising/fun this week_ | — |",
         ""]

    refresh = sorted([c for c in cands if c.get("action") == "refresh"],
                     key=lambda c: abs(c["evidence"]["live"] - c["evidence"]["printed"]),
                     reverse=True)
    if refresh:
        L += [f"### 🔄 Star refreshes ({len(refresh)} stale)", "",
              "| Repo | README | Live | Δ |", "|------|--------|------|---|"]
        for c in refresh:
            ev = c["evidence"]
            d = ev["live"] - ev["printed"]
            L.append(f"| [{c['id']}]({c['url']}) | {ev['printed']} | {ev['live']} | {d:+d} |")
        L.append("")

    new_repos = [c for c in cands if c["kind"] == "repo" and c["action"] == "add"]
    if new_repos:
        L += [f"### 🆕 New tooling candidates ({len(new_repos)})", "",
              "| Repo | ⭐ | Description |", "|------|---|-------------|"]
        for c in new_repos[:10]:
            L.append(f"| [{c['id']}]({c['url']}) | {c['score']} | {c['evidence'].get('desc','')} |")
        L.append("")

    new_papers = [c for c in cands if c["kind"] == "paper" and c["action"] == "add"]
    if new_papers:
        L += [f"### 📄 New paper candidates ({len(new_papers)})", "",
              "| Paper | Date |", "|-------|------|"]
        for c in new_papers[:12]:
            L.append(f"| [{c['title']}]({c['url']}) | {c['evidence'].get('published','')} |")
        L.append("")

    L += ["---", "_Generated by the RSI auto-sync pipeline. No item is added until "
          "you merge this PR._"]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="knowledge/candidates.*.json")
    ap.add_argument("--week", default="this week")
    ap.add_argument("--pr-body", default="/tmp/pr_body.md")
    ap.add_argument("--out", default="knowledge/candidates.json")
    args = ap.parse_args()

    cands = load_candidates(args.glob)
    slate = pick_slate(cands)
    body = render_pr_body(args.week, cands, slate)

    open(args.pr_body, "w", encoding="utf-8").write(body)
    json.dump({"week": args.week, "candidates": cands},
              open(args.out, "w", encoding="utf-8"), indent=2)

    n_award = sum(1 for v in slate.values() if v)
    print(f"✓ {len(cands)} candidates · {n_award}/5 award slots filled", file=sys.stderr)
    print(f"  PR body → {args.pr_body}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
