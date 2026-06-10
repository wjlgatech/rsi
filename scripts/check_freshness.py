#!/usr/bin/env python3
"""check_freshness.py — verify every link in a markdown file is still alive.

Zero external deps (stdlib only) so it runs in any CI. Designed for awesome-list
freshness checks: extract every http(s) link, probe each concurrently (HEAD, falling
back to GET on 405/403), and report the dead ones with their status.

Domains that block bots (x.com, linkedin.com, scholar.google.com) are probed but
failures there are reported as WARN, not DEAD — they never fail the run.

Usage:
  check_freshness.py README.md [--report report.md] [--timeout 15] [--max-workers 12]

Exit codes: 0 = all good (warnings allowed) · 1 = at least one dead link.
"""

from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

# These reject anonymous probes; a failure proves nothing about the link.
_BOT_WALLED = (
    "x.com", "twitter.com", "linkedin.com", "scholar.google.com", "openreview.net",
    "img.shields.io", "openai.com",
)
_UA = "Mozilla/5.0 (compatible; awesome-freshness-check/1.0; +https://github.com)"


def probe(url: str, timeout: int) -> tuple[str, int | str]:
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": _UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return url, r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 429):
                continue
            return url, e.code
        except Exception as e:  # DNS, timeout, TLS, redirect loops
            if method == "HEAD":
                continue
            return url, type(e).__name__
    return url, "unreachable"


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    path, report, timeout, workers = args[0], "", 15, 12
    it = iter(args[1:])
    for a in it:
        if a == "--report":
            report = next(it, "")
        elif a == "--timeout":
            timeout = int(next(it, "15"))
        elif a == "--max-workers":
            workers = int(next(it, "12"))

    md = open(path, encoding="utf-8", errors="ignore").read()
    urls = sorted({u.rstrip(").,}\\") for u in re.findall(r"https?://[^\s)\"'<>\]}]+", md)})
    print(f"probing {len(urls)} unique links from {path} …", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda u: probe(u, timeout), urls))

    ok, warn, dead = [], [], []
    for url, status in results:
        good = isinstance(status, int) and status < 400
        if good:
            ok.append((url, status))
        elif any(d in url for d in _BOT_WALLED):
            warn.append((url, status))
        else:
            dead.append((url, status))

    lines = [
        f"# Link freshness report",
        f"",
        f"**{len(ok)} alive · {len(warn)} bot-walled (unverifiable) · {len(dead)} dead** "
        f"of {len(urls)} unique links in `{path}`.",
    ]
    if dead:
        lines += ["", "## ❌ Dead links", ""] + [f"- `{s}` — {u}" for u, s in dead]
    if warn:
        lines += ["", "## ⚠️ Unverifiable (bot-walled domains)", ""] + [
            f"- `{s}` — {u}" for u, s in warn
        ]
    out = "\n".join(lines)
    print(out)
    if report:
        open(report, "w").write(out + "\n")
    sys.exit(1 if dead else 0)


if __name__ == "__main__":
    main()
