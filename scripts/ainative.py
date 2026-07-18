#!/usr/bin/env python3
"""AI-native self-audit — score rsi's own operation against the loop-engineering
and physical-ai-native principles (data/ainative.yml), from real evidence in this repo.

A principle's evidence is a `file` that must exist or a `grep` regex that must be
found in a file. Score = mean fraction of evidence present. Discipline: no evidence
⇒ the principle fails (never a fake pass). `--gate N` exits non-zero below N so CI
can block a regression in how AI-native the operation is.

  ainative.py [--json] [--gate N]
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from rsidata import DATA, ROOT, load


def _has(item: dict) -> bool:
    """True if the evidence exists: a file/dir present, or a regex found in a file."""
    target = ROOT / item["file"]
    if not target.exists():
        return False
    if "grep" not in item:
        return True  # bare file/dir existence is the evidence
    try:
        text = target.read_text(errors="ignore") if target.is_file() else ""
    except OSError:
        return False
    return re.search(item["grep"], text) is not None


class AINativeAudit:
    """Evaluate each principle's evidence and roll up an AI-native score."""

    def __init__(self) -> None:
        self.rubric = load("ainative")

    def run(self) -> dict:
        principles = []
        for p in self.rubric["principles"]:
            ev = p.get("evidence", [])
            present = [_has(e) for e in ev]
            frac = sum(present) / len(ev) if ev else 0.0
            status = "met" if frac == 1 else "partial" if frac > 0 else "fail"
            principles.append({
                "id": p["id"], "statement": p["statement"], "source": p.get("source", ""),
                "status": status, "fraction": round(frac, 2),
                "missing": [ev[i].get("grep", ev[i]["file"]) for i, ok in enumerate(present) if not ok],
            })
        score = round(100 * sum(p["fraction"] for p in principles) / len(principles)) if principles else 0
        return {"score": score, "pass_threshold": self.rubric.get("pass_threshold", 85), "principles": principles}


ICON = {"met": "✅", "partial": "🟡", "fail": "❌"}


def print_human(r: dict) -> None:
    """Print the audit as a per-principle scorecard."""
    verdict = "AI-NATIVE" if r["score"] >= r["pass_threshold"] else "NOT YET"
    print(f"AI-native self-audit: {r['score']}/100  (threshold {r['pass_threshold']}) — {verdict}\n")
    for p in r["principles"]:
        print(f"  {ICON[p['status']]} {p['id']:<24} {int(p['fraction']*100):>3}%  [{p['source']}]")
        if p["missing"]:
            print(f"       missing: {', '.join(p['missing'])}")


def main() -> int:
    """CLI: audit this repo's AI-native operation; --gate N fails below the bar."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--gate", type=int)
    args = ap.parse_args()

    r = AINativeAudit().run()
    print(json.dumps(r, indent=2) if args.json else "", end="")
    if not args.json:
        print_human(r)
    gate = args.gate if args.gate is not None else None
    if gate is not None and r["score"] < gate:
        print(f"\n::gate:: FAILED — AI-native score {r['score']} < {gate}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
