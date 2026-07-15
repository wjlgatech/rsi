#!/usr/bin/env python3
"""certify.py — the RSI tooling certification engine (a ClosedLoop, not a popularity list).

skills.sh ranks tooling by install count. That's popularity, and popularity is gameable and
says nothing about whether a tool WORKS, is SAFE, or is MAINTAINED. This is the layer it lacks:
each RSI tool earns an evidence-backed certification across a fixed rubric. The rubric is DATA
(one source of truth), evidence is COLLECTED (never claimed), and the honesty rules are load-
bearing — a dimension with no evidence is "not_measured" (NOT a pass), and the top tier can never
be granted on an unmeasured blocking dimension. Exit non-zero when a --gate tier isn't met, so it
gates CI like `anyagent brace`.

The deep dimensions (Works, Safe, Quality) are designed to be filled by the anyagent primitives
the repo already owns — `anyagent analyze` (quality), `anyagent brace` (BRACE security),
a smoke install (Works). Until those run for a tool, they are honestly "not_measured", and the
tool tops out at 🥈 Verified — never 🥇 Certified.

Usage:
  certify.py --graph knowledge/graph.json --candidates knowledge/candidates.json \\
             --out knowledge/certifications.json [--gate verified]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

# ── The rubric, as data (single source of truth) ─────────────────────────────
# Each dimension: how it's measured, whether it blocks the badge, and its pass bar.
# `source` names the evidence collector — signals we HAVE today vs anyagent-driven
# checks that are honestly not_measured until run.
RUBRIC = [
    {"key": "relevant",   "label": "RSI-relevant",  "blocking": True,  "source": "lexicon"},
    {"key": "maintained", "label": "Maintained",    "blocking": True,  "source": "pushed_at"},
    {"key": "adopted",    "label": "Adopted",       "blocking": False, "source": "stars"},
    {"key": "works",      "label": "Works (repro)", "blocking": True,  "source": "anyagent-analyze"},
    {"key": "safe",       "label": "Safe (BRACE)",  "blocking": True,  "source": "anyagent-brace"},
]

RSI_LEXICON = ("self-improv", "self-evolv", "recursive self", "godel", "gödel", "ai scientist",
               "automated research", "research agent", "open-ended", "meta-learning",
               "agentic system", "self-referential", "scientific discovery", "reward design",
               "curriculum", "evolutionary", "benchmark", "agent")

NOT_MEASURED = "not_measured"


def _relevant(name: str, summary: str) -> int:
    blob = f"{name} {summary}".lower()
    hits = sum(1 for t in RSI_LEXICON if t in blob)
    return min(100, hits * 40) if hits else 0


def _maintained(pushed: str | None, today: dt.date) -> int | str:
    if not pushed:
        return NOT_MEASURED
    try:
        days = (today - dt.date.fromisoformat(pushed[:10])).days
    except ValueError:
        return NOT_MEASURED
    if days <= 180:
        return 100
    if days <= 365:
        return 60
    return 20  # >1yr since a push — measured, but weak


def _adopted(stars: int | None) -> int | str:
    if not stars:
        return NOT_MEASURED
    # log-ish bands: 100+ = on the map, 1k+ = strong, 10k+ = flagship
    return 100 if stars >= 10000 else 80 if stars >= 1000 else 60 if stars >= 100 else 40


def tier(scores: dict) -> str:
    """Honest badge. 🥇 requires EVERY blocking dim measured AND passing; 🥈 requires the
    signals we can measure today; else 🥉 listed. no-evidence on a blocking dim ⇒ never 🥇."""
    blocking = [d for d in RUBRIC if d["blocking"]]
    measured_pass = lambda d: isinstance(scores[d["key"]], int) and scores[d["key"]] >= 60
    if all(measured_pass(d) for d in blocking):
        return "🥇 RSI-Certified"
    # 🥈 Verified: the *available* blocking dims (relevant + maintained) pass; the anyagent
    # dims may still be not_measured (that's why it's not yet 🥇).
    available = [d for d in blocking if d["source"] not in ("anyagent-analyze", "anyagent-brace")]
    if available and all(measured_pass(d) for d in available):
        return "🥈 Verified"
    return "🥉 Listed"


def certify_tool(node: dict, today: dt.date) -> dict:
    """Certify one normalized tool node: {id,name,url,category,summary,stars,pushed,kind,curated}."""
    # Curated tools (already in the human-vetted list) get a relevance floor — a human
    # already decided they belong, so a terse summary can't disqualify them (fixes the
    # dspy="Declarative LM"→0 false-negative). New candidates must earn relevance via lexicon.
    rel = _relevant(node["name"], node.get("summary", ""))
    if node.get("curated"):
        rel = max(rel, 60)
    scores = {
        "relevant": rel,
        "maintained": _maintained(node.get("pushed"), today),
        "adopted": _adopted(node.get("stars")),
        "works": NOT_MEASURED,   # ← fill via `anyagent analyze <clone>` / smoke install
        "safe": NOT_MEASURED,    # ← fill via `anyagent brace <manifest>`
    }
    return {
        "id": node["id"], "name": node["name"], "url": node.get("url", ""),
        "kind": node.get("kind", "repo"), "category": node.get("category", ""),
        "tier": tier(scores), "scores": scores,
        "evidence": {"stars": node.get("stars"), "pushed": node.get("pushed")},
    }


def _dist(certs: list[dict]) -> dict:
    from collections import Counter
    return Counter(c["tier"] for c in certs)


def render_table(certs: list[dict], today: dt.date) -> str:
    """The FULL certified-tooling table — lives in docs/CERTIFIED.md + the weekly PR body.
    Kept OUT of the README on purpose: awesome_kg parses every pipe table into graph nodes,
    so an in-README table would pollute the knowledge graph."""
    L = [f"# 🏅 RSI Certified Tooling  ·  _auto-updated {today.isoformat()}_", "",
         "Every tool earns an **evidence-backed** tier — not an install count "
         "(that's the layer [skills.sh](https://www.skills.sh/) lacks). "
         "🥉 Listed · 🥈 Verified (relevant + maintained, machine-checked) · "
         "🥇 RSI-Certified (adds *works* + *safe* via `anyagent analyze`/`brace`). "
         "No-evidence ⇒ no badge. Machine-readable: [`knowledge/certifications.json`](../knowledge/certifications.json).", "",
         "| Tier | Name | Kind | ⭐ | Signals |", "|------|------|------|---|---------|"]
    for c in certs:
        s = c["scores"]
        sig = f"rel {s['relevant']} · maint {s['maintained']} · adopt {s['adopted']}"
        stars = c["evidence"].get("stars") or "—"
        L.append(f"| {c['tier']} | [{c['name']}]({c['url']}) | {c['kind']} | {stars} | {sig} |")
    return "\n".join(L) + "\n"


def render_summary(certs: list[dict], today: dt.date) -> str:
    """The compact README block — counts + link, NO table (so the graph stays clean)."""
    d = _dist(certs)
    return "\n".join([
        START + " (generated by scripts/certify.py — do not edit by hand) -->",
        "### 🏅 Certified Tooling",
        "",
        "Tools here earn an **evidence-backed** tier, not an install count — the trust layer "
        "[skills.sh](https://www.skills.sh/) lacks. "
        f"**{d.get('🥇 RSI-Certified', 0)} 🥇 Certified · {d.get('🥈 Verified', 0)} 🥈 Verified · "
        f"{d.get('🥉 Listed', 0)} 🥉 Listed** as of {today.isoformat()}.",
        "",
        "🥈 Verified = relevant + maintained (machine-checked). 🥇 adds *works* + *safe* "
        "via `anyagent analyze`/`brace`; no-evidence ⇒ no badge. "
        "→ **[Full certified list](docs/CERTIFIED.md)** · [raw data](knowledge/certifications.json)",
        "",
        END,
    ])


START = "<!-- CERTIFIED-TOOLING:START"
END = "<!-- CERTIFIED-TOOLING:END -->"
# Insert here the first time (end of the Tools section) if the markers aren't present yet.
ANCHOR = "## 👥 People & Labs to Follow"


def inject_readme(path: str, block: str) -> None:
    """Idempotently fold the certified-tooling block into the README: replace between
    the markers if present, else insert just before the People & Labs section."""
    import re
    text = open(path, encoding="utf-8").read()
    if START in text and END in text:
        new = re.sub(re.escape(START) + r".*?" + re.escape(END), block, text, flags=re.DOTALL)
    elif ANCHOR in text:
        new = text.replace(ANCHOR, f"{block}\n\n---\n\n{ANCHOR}", 1)
    else:
        new = text.rstrip() + "\n\n" + block + "\n"
    if new != text:
        open(path, "w", encoding="utf-8").write(new)
        print(f"  ↳ folded certified-tooling block into {path}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default="knowledge/graph.json")
    ap.add_argument("--candidates", default="knowledge/candidates.json")
    ap.add_argument("--out", default="knowledge/certifications.json")
    ap.add_argument("--markdown", default=None, help="also write a README/PR certified-tooling table")
    ap.add_argument("--inject", default=None, help="fold the table into this README (idempotent, between markers)")
    ap.add_argument("--gate", choices=["listed", "verified", "certified"], default=None,
                    help="exit non-zero if ANY tool fails to reach this tier (CI gate)")
    ap.add_argument("--today", default=None)
    args = ap.parse_args()

    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    graph = json.load(open(args.graph, encoding="utf-8"))
    raw_cands = []
    try:
        with open(args.candidates, encoding="utf-8") as f:
            raw_cands = json.load(f).get("candidates", [])
    except (OSError, json.JSONDecodeError):
        pass
    live = {c["url"]: c["evidence"] for c in raw_cands
            if c.get("kind") == "repo" and c.get("action") == "refresh" and c.get("evidence")}

    # Curated graph repos …
    tools, seen = [], set()
    for n in graph["nodes"]:
        if n["type"] != "repo":
            continue
        url = (n.get("links") or [""])[0]
        ev = live.get(url, {})
        tools.append({"id": n["id"], "name": n["name"], "url": url, "kind": "repo",
                      "category": n.get("category", ""), "summary": n.get("summary", ""),
                      "stars": ev.get("live", n.get("stars")), "pushed": ev.get("pushed"),
                      "curated": True})
        seen.add(url)
    # … plus newly-discovered tooling: skills (unit 1), MCP servers (unit 3), workflows
    # (unit 4), and repo discoveries — every kind joins here through the same schema.
    CATEGORY = {"skill": "🧩 Agent Skill", "mcp": "🔌 MCP Server",
                "workflow": "🔀 Workflow", "repo": "🆕 Tool"}
    for c in raw_cands:
        if c.get("action") != "add" or c.get("kind") not in CATEGORY or c.get("url") in seen:
            continue
        seen.add(c["url"])
        e = c.get("evidence", {})
        tools.append({"id": c["id"], "name": c.get("title", c["id"]), "url": c["url"],
                      "kind": c["kind"], "category": CATEGORY[c["kind"]],
                      "summary": e.get("desc", ""), "stars": e.get("stars", c.get("score")),
                      "pushed": e.get("pushed"), "curated": False})

    certs = [certify_tool(t, today) for t in tools]
    TIER_RANK = {"🥇 RSI-Certified": 2, "🥈 Verified": 1, "🥉 Listed": 0}
    certs.sort(key=lambda c: (TIER_RANK[c["tier"]], c["evidence"].get("stars") or 0), reverse=True)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"rubric": RUBRIC, "certifications": certs}, f, indent=2)

    if args.markdown:  # the FULL table → docs/CERTIFIED.md + the PR body
        with open(args.markdown, "w", encoding="utf-8") as f:
            f.write(render_table(certs, today))
    if args.inject:    # the compact summary (no table) → README, keeps the graph clean
        inject_readme(args.inject, render_summary(certs, today))

    from collections import Counter
    dist = Counter(c["tier"] for c in certs)
    print(f"✓ certified {len(certs)} tools ({sum(1 for t in tools if t['kind']=='skill')} skills) → {args.out}", file=sys.stderr)
    for t in ["🥇 RSI-Certified", "🥈 Verified", "🥉 Listed"]:
        print(f"  {t}: {dist.get(t, 0)}", file=sys.stderr)

    if args.gate:
        order = {"listed": 0, "verified": 1, "certified": 2}
        rank = {"🥉 Listed": 0, "🥈 Verified": 1, "🥇 RSI-Certified": 2}
        below = [c for c in certs if rank[c["tier"]] < order[args.gate]]
        if below:
            print(f"\n✗ gate '{args.gate}': {len(below)} tool(s) below bar", file=sys.stderr)
            for c in below[:8]:
                print(f"  - {c['name']} ({c['tier']})", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
