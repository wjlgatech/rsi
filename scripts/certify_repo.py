#!/usr/bin/env python3
"""RSI-Certified — score an AI-Scientist-style repo against data/certify.yml.

  certify_repo.py --target <dir|github-url> [--gate N] [--badge out.json] [--json]

STATIC ONLY (v0.1): it reads the code, never runs it — the whole point, since
executing a self-modifying research agent to "prove" it is the risk, not the proof.
Discipline: evidence over claims; a dimension with no evidence is not-measured and
excluded from the score (never a fake pass); a blocking gate (safety, relevance)
cannot pass on unmeasured items; --gate exits non-zero so it gates CI.

This is the DEEP, per-repo rubric certifier (the badge a tool author earns). It is
complementary to scripts/certify.py, which is the fast signals roll-up across the
whole listed registry. Rubric lives in data/certify.yml (single source of truth).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

from rsidata import ROOT, load

RUBRIC = load("certify")
TEXT_EXT = {".md", ".py", ".sh", ".js", ".ts", ".yml", ".yaml", ".json", ".toml", ".txt", ".cfg", ".ipynb"}
DOC_NAMES = ("README.md", "readme.md", "README.rst", "SKILL.md")


class Dim:
    def __init__(self, score: int | None, evidence: str, measured: bool = True) -> None:
        self.score = score
        self.evidence = evidence
        self.measured = measured and score is not None


def gather(target: pathlib.Path):
    files, blob, doc, names = [], [], None, set()
    for p in sorted(target.rglob("*")):
        if p.is_file() and ".git" not in p.parts:
            names.add(p.name)
        if not (p.is_file() and p.suffix.lower() in TEXT_EXT and ".git" not in p.parts):
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        files.append(p)
        blob.append(text[:200_000])
        if doc is None and p.name in DOC_NAMES:
            doc = (p, text)
    return files, "\n".join(blob), doc, names


class Certifier:
    def __init__(self, target: pathlib.Path) -> None:
        self.target = target
        self.files, self.blob, self.doc, self.names = gather(target)
        self.lc = self.blob.lower()

    @property
    def name(self) -> str:
        return self.target.name

    def _safety(self) -> Dim:
        cfg = RUBRIC["safety"]
        crit = [p for p in cfg["critical_patterns"] if re.search(p, self.blob)]
        if crit:
            return Dim(0, f"CRITICAL: dangerous pattern — {crit[0][:40]}")
        warn = [p for p in cfg["warn_patterns"] if re.search(p, self.blob)]
        score = max(0, 100 - 15 * len(warn))
        notes = [f"{len(warn)} warning(s)"] if warn else ["clean"]
        # RSI-specific: model-generated-code execution demands a visible checker/sandbox.
        self_exec = [p for p in cfg["self_exec_patterns"] if re.search(p, self.blob, re.I)]
        if self_exec:
            has_checker = any(s in self.lc for s in cfg["checker_signals"])
            if has_checker:
                notes.append("self-exec present + checker/sandbox signalled")
            else:
                score = min(score, 45)
                notes.append("⚠ self-modifying/exec of generated code with NO maker≠checker signal")
        return Dim(score, "; ".join(notes))

    def _relevance(self) -> Dim:
        hits = sorted({k for k in RUBRIC["relevance"]["keywords"] if k in self.lc})
        ev = f"{len(hits)} RSI keyword(s): {', '.join(hits[:6])}" if hits else "no on-mission keywords"
        return Dim(min(100, len(hits) * 16), ev)

    def _reproducibility(self) -> Dim:
        sig = RUBRIC["signals"]
        rf = [f for f in sig["repro_files"] if f in self.names]
        kw = [s for s in sig["reproducibility"] if s in self.lc]
        has_tests = any(n in self.names for n in ("tests", "test")) or bool(
            re.search(r"(test_.*\.py|def test_|\.test\.)", self.blob))
        score = min(100, len(rf) * 22 + len(kw) * 6 + (20 if has_tests else 0))
        ev = f"{len(rf)} manifest file(s) ({', '.join(rf[:3]) or '—'}), {len(kw)} run-signal(s)" + (", tests" if has_tests else ", no tests")
        return Dim(score, ev)

    def _autonomy(self) -> Dim:
        hits = [s for s in RUBRIC["signals"]["autonomy"] if s in self.lc]
        ev = f"{len(hits)} autonomy signal(s): {', '.join(hits[:6])}" if hits else "no autonomy signals"
        return Dim(min(100, len(hits) * 14), ev)

    def _eval(self) -> Dim:
        hits = [s for s in RUBRIC["signals"]["eval"] if s in self.lc]
        named = [b for b in ("mlagentbench", "mle-bench", "swe-bench", "re-bench", "tgb") if b in self.lc]
        score = min(100, len(hits) * 12 + len(named) * 25)
        ev = f"eval signals: {', '.join(hits[:5]) or 'none'}" + (f" · named benchmark(s): {', '.join(named)}" if named else "")
        return Dim(score, ev)

    def _provenance(self) -> Dim:
        h = hashlib.sha256()
        for p in sorted(self.files):
            try:
                h.update(p.read_bytes())
            except OSError:
                pass
        # A git remote (source) present raises provenance; author unknown from static files.
        src = (self.target / ".git").exists()
        score = 40 + (30 if src else 0)
        return Dim(score, f"content-hash {h.hexdigest()[:16]}" + ("; git source present" if src else "; no declared source"))

    def _docs(self) -> Dim:
        if not self.doc:
            return Dim(0, "no README/SKILL present")
        text = self.doc[1].lower()
        score, notes = 40, ["doc present"]
        if any(s in text for s in ("## ", "# ", "description", "overview")):
            score += 20; notes.append("description")
        if any(s in text for s in ("install", "usage", "how to run", "quick start", "getting started")):
            score += 20; notes.append("how-to-run")
        if "```" in text or "example" in text:
            score += 20; notes.append("example")
        return Dim(min(score, 100), "; ".join(notes))

    def _cross_runtime(self) -> Dim:
        hits = [s for s in RUBRIC["signals"]["cross_runtime"] if s in self.lc]
        if not hits:
            return Dim(50, "single-runtime (no portability signal)")
        return Dim(min(100, 55 + 12 * len(hits)), f"portability: {', '.join(sorted(set(hits))[:5])}")

    def run(self) -> dict:
        dims = {
            "safety": self._safety(), "reproducibility": self._reproducibility(),
            "relevance": self._relevance(), "autonomy": self._autonomy(),
            "eval": self._eval(), "provenance": self._provenance(),
            "docs": self._docs(), "cross_runtime": self._cross_runtime(),
        }
        weights = {d["id"]: d["weight"] for d in RUBRIC["dimensions"]}
        mw = sum(weights[k] for k, d in dims.items() if d.measured)
        score = round(sum(weights[k] * d.score for k, d in dims.items() if d.measured) / mw) if mw else 0
        sec, rel = dims["safety"], dims["relevance"]
        safety_ok = bool(sec.measured and sec.score >= RUBRIC["gates"]["safety"]["min"])
        on_mission = bool(rel.measured and rel.score >= RUBRIC["gates"]["relevance"]["min"])
        return {
            "name": self.name, "score": score,
            "tier": decide_tier(score, safety_ok, on_mission),
            "safety_ok": safety_ok, "on_mission": on_mission,
            "dimensions": {k: {"score": d.score, "measured": d.measured, "evidence": d.evidence} for k, d in dims.items()},
            "gaps": [f"{k} ({d.score})" for k, d in dims.items() if d.measured and d.score < 60],
        }


def decide_tier(score: int, safety_ok: bool, on_mission: bool) -> str:
    if not on_mission:
        return "not-applicable"
    if not safety_ok:
        return "rejected"
    if score >= RUBRIC["tiers"]["certified"]:
        return "certified"
    if score >= RUBRIC["tiers"]["provisional"]:
        return "provisional"
    return "rejected"


def badge(r: dict) -> dict:
    color = {"certified": "brightgreen", "provisional": "yellow",
             "rejected": "red", "not-applicable": "lightgrey"}[r["tier"]]
    msg = f"{r['tier']} · {r['score']}/100" if r["tier"] in ("certified", "provisional") else r["tier"]
    return {"schemaVersion": 1, "label": "RSI-Certified", "message": msg, "color": color}


def certify_target(target: str) -> dict:
    """Certify a local dir or a github URL (shallow-cloned to a throwaway tempdir)."""
    if re.match(r"^https?://", target):
        tmp = tempfile.mkdtemp(prefix="rsi-cert-")
        try:
            r = subprocess.run(["git", "clone", "--depth", "1", "--quiet", target, tmp],
                               capture_output=True, text=True, timeout=180)
            if r.returncode != 0:
                raise RuntimeError(f"clone failed: {r.stderr.strip()[:120]}")
            result = Certifier(pathlib.Path(tmp)).run()
            result["name"] = target.rstrip("/").removesuffix(".git").split("github.com/")[-1]
            return result
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return Certifier(pathlib.Path(target).resolve()).run()


def print_human(r: dict) -> None:
    icon = {"certified": "✅", "provisional": "🟡", "rejected": "❌", "not-applicable": "⚪"}[r["tier"]]
    print(f"{icon}  {r['name']} — {r['tier'].upper()}  score {r['score']}/100")
    for k, d in r["dimensions"].items():
        s = f"{d['score']:>3}" if d["measured"] else " NM"
        print(f"    {s}  {k:<15} {d['evidence']}")
    if r["gaps"]:
        print(f"    ↑ improve: {', '.join(r['gaps'])}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, help="local dir or github URL")
    ap.add_argument("--gate", type=int, help="exit non-zero if score < N or a blocking gate fails")
    ap.add_argument("--badge")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    r = certify_target(args.target)
    if args.badge:
        pathlib.Path(args.badge).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.badge).write_text(json.dumps(badge(r)))
    if args.json:
        print(json.dumps(r, indent=2))
    else:
        print_human(r)
    if args.gate is not None:
        if not r["on_mission"]:
            print("::gate:: FAILED — not on-mission (relevance gate)", file=sys.stderr)
            return 1
        if not r["safety_ok"] or r["score"] < args.gate:
            print(f"::gate:: FAILED — score {r['score']} < {args.gate} or safety gate", file=sys.stderr)
            return 1
        print(f"::gate:: PASSED — score {r['score']} >= {args.gate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
