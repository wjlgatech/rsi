#!/usr/bin/env python3
"""certify_gold.py — the 🥇 tier: fill `works` + `safe` from a real clone.

The signals tier (certify.py) gets a tool to 🥈 Verified. 🥇 RSI-Certified needs the two
blocking dims certify.py leaves `not_measured`:

  works  ← `anyagent analyze <clone>` — a STATIC OOP/quality read (it reads code, never
           runs it, so it's safe to point at an untrusted repo).
  safe   ← a static safety scan (committed-secret patterns, remote-exec pipelines,
           over-broad permissions). Also read-only — nothing from the clone executes.

"Sandbox" here = a throwaway shallow clone in a tempdir + STATIC analysis only. We never
install or run the cloned code — that's the whole point (executing untrusted tooling to
"prove it works" is the risk, not the proof). Results merge back into certifications.json
and re-tier via certify.tier(); docs/README refresh so 🥇 badges go live through the PR.

Usage:
  certify_gold.py --certs knowledge/certifications.json --top 3   # deep-check top Verified
  certify_gold.py --slugs jennyzzt/dgm eureka-research/Eureka
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import certify as C  # reuse tier(), render_table(), render_summary(), inject_readme()

# Static safety scan: patterns that make a tool risky to install/run. Read-only grep.
_SECRET_RX = re.compile(r"(sk-[A-Za-z0-9]{20,}|nvapi-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36})")
_RISKY_RX = [
    re.compile(r"curl\s+[^\n|]*\|\s*(sudo\s+)?(ba)?sh"),      # curl … | sh
    re.compile(r"eval\s*\(\s*(base64|atob|exec|require\(['\"]child_process)"),
    re.compile(r"os\.system\(|subprocess\.(Popen|call|run)\([^)]*shell\s*=\s*True"),
    re.compile(r"rm\s+-rf\s+[~/]"),
]
_TEXT_EXT = (".py", ".js", ".ts", ".tsx", ".sh", ".md", ".json", ".yaml", ".yml", ".toml", ".env")


def clone(url: str, dest: str) -> bool:
    r = subprocess.run(["git", "clone", "--depth", "1", "--quiet", url, dest],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"  ! clone failed: {r.stderr.strip()[:120]}", file=sys.stderr)
    return r.returncode == 0


def score_works(clone_dir: str) -> int | str:
    """`anyagent analyze` OOP/quality (static). Parse 'OOP quality: N/100'."""
    exe = shutil.which("anyagent")
    if not exe:
        return C.NOT_MEASURED
    try:
        r = subprocess.run([exe, "analyze", clone_dir], capture_output=True, text=True, timeout=300)
    except (subprocess.TimeoutExpired, OSError):
        return C.NOT_MEASURED
    m = re.search(r"quality:\s*(\d+)\s*/\s*100", r.stdout + r.stderr)
    return int(m.group(1)) if m else C.NOT_MEASURED


def score_safe(clone_dir: str) -> tuple[int, list[str]]:
    """Static safety scan (read-only). Start at 100; deduct per risk. Never runs the code."""
    findings, secrets, risky = [], 0, 0
    for root, dirs, files in os.walk(clone_dir):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", ".venv", "dist", "build")]
        for fn in files:
            if not fn.lower().endswith(_TEXT_EXT):
                continue
            p = os.path.join(root, fn)
            try:
                with open(p, encoding="utf-8", errors="ignore") as f:
                    text = f.read(200_000)
            except OSError:
                continue
            rel = os.path.relpath(p, clone_dir)
            if _SECRET_RX.search(text):
                secrets += 1
                findings.append(f"committed secret pattern in {rel}")
            for rx in _RISKY_RX:
                if rx.search(text):
                    risky += 1
                    findings.append(f"risky exec pattern in {rel}")
                    break
    score = max(0, 100 - secrets * 60 - risky * 20)  # a committed secret is near-disqualifying
    return score, findings[:8]


def deep_certify(cert: dict) -> dict:
    url = cert.get("url", "")
    if not url.startswith("https://github.com/"):
        return cert
    tmp = tempfile.mkdtemp(prefix="rsi-gold-")
    try:
        if not clone(url, tmp):
            return cert
        works = score_works(tmp)
        safe, findings = score_safe(tmp)
        cert["scores"]["works"] = works
        cert["scores"]["safe"] = safe
        cert["tier"] = C.tier(cert["scores"])
        cert.setdefault("evidence", {})["deep"] = {"works": works, "safe": safe, "safety_findings": findings}
        badge = cert["tier"]
        print(f"  {cert['name']}: works={works} safe={safe} → {badge}"
              + (f"  ⚠ {findings[0]}" if findings else ""), file=sys.stderr)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return cert


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--certs", default="knowledge/certifications.json")
    ap.add_argument("--top", type=int, default=0, help="deep-check the top N 🥈 Verified tools")
    ap.add_argument("--slugs", nargs="*", default=[], help="specific owner/repo(s) to deep-check")
    ap.add_argument("--markdown", default="docs/CERTIFIED.md")
    ap.add_argument("--inject", default="README.md")
    args = ap.parse_args()

    import datetime as dt
    data = json.load(open(args.certs, encoding="utf-8"))
    certs = data["certifications"]

    targets = []
    if args.slugs:
        targets = [c for c in certs if any(c["url"].endswith("/" + s) or s in c["id"] for s in args.slugs)]
    elif args.top:
        targets = [c for c in certs if c["tier"] == "🥈 Verified"][:args.top]
    if not targets:
        print("no targets (use --top N or --slugs owner/repo)", file=sys.stderr)
        return 1

    print(f"🥇 deep-certifying {len(targets)} tool(s) via clone + anyagent analyze + safety scan",
          file=sys.stderr)
    for c in targets:
        deep_certify(c)

    from collections import Counter
    dist = Counter(c["tier"] for c in certs)
    today = dt.date.today()
    with open(args.certs, "w", encoding="utf-8") as f:
        json.dump({"rubric": data.get("rubric"), "certifications": certs}, f, indent=2)
    if args.markdown:
        open(args.markdown, "w", encoding="utf-8").write(C.render_table(certs, today))
    if args.inject:
        C.inject_readme(args.inject, C.render_summary(certs, today))
    print(f"✓ {dist.get('🥇 RSI-Certified',0)} 🥇 · {dist.get('🥈 Verified',0)} 🥈 · {dist.get('🥉 Listed',0)} 🥉",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
