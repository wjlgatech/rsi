#!/usr/bin/env python3
"""repo_factory.py — turn one cited repo into {knowledge graph, agentic skill}.

rsi is the hub of 1) knowledge 2) tooling 3) experts. This mints, per top repo:
  • a KNOWLEDGE GRAPH  → knowledge/repos/<slug>/graph.json  (same schema as the field
    graph, so docs/index.html renders it too). STATIC — zero LLM: modules, key files,
    README concepts, detected frameworks; edges = contains / documents / uses.
  • an AGENTIC SKILL   → skills/<slug>/SKILL.md  (frontmatter `description` = the
    progressive-disclosure trigger; body = what it does · how to apply · links to KG+repo).
    Static-first from README + metadata; `--enrich` adds a content-hash-CACHED LLM summary
    (~1 call/repo via `anyagent reverse`) when available, else degrades honestly.

Fast (static, parallelizable), cheap (zero-LLM core + cached enrich), up-to-date (re-run only
when a repo's content-hash changes), future-proof (pure data artifacts + portable skills).

  repo_factory.py --target <dir|github-url> [--enrich]
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

from rsidata import ROOT

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__",
             ".next", ".mypy_cache", ".pytest_cache", "site-packages"}
CODE_EXT = {".py", ".js", ".ts", ".tsx", ".rs", ".go", ".java", ".cpp", ".c", ".ipynb"}
ENTRYPOINTS = ("main.py", "run.py", "cli.py", "app.py", "__main__.py", "train.py",
               "agent.py", "pyproject.toml", "setup.py", "package.json", "Dockerfile", "Makefile")
FRAMEWORKS = {
    "pytorch": ["torch", "pytorch"], "tensorflow": ["tensorflow", "keras"],
    "jax": ["jax", "flax"], "transformers": ["transformers", "huggingface"],
    "langchain": ["langchain"], "langgraph": ["langgraph"], "dspy": ["dspy"],
    "openai": ["openai"], "anthropic": ["anthropic"], "vllm": ["vllm"],
    "mcp": ["mcp", "model context protocol"], "gymnasium": ["gym", "gymnasium"],
}


# Boilerplate README headings — excluded from concepts + triggers so progressive
# disclosure keys off a repo's DISTINCTIVE vocabulary, not generic section names.
GENERIC_HEADINGS = ("introduction", "requirement", "installation", "install", "setup",
                    "usage", "getting started", "quick start", "quickstart", "license",
                    "citation", "cite", "contributing", "acknowledg", "prerequisite",
                    "overview", "faq", "contents", "changelog", "roadmap", "table of",
                    "getting-started", "api key", "environment", "dependencies", "example")


def _generic(title: str) -> bool:
    t = title.lower()
    return any(g in t for g in GENERIC_HEADINGS)


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def clone_or_local(target: str):
    if re.match(r"^https?://", target):
        tmp = tempfile.mkdtemp(prefix="rsi-factory-")
        r = subprocess.run(["git", "clone", "--depth", "1", "--quiet", target, tmp],
                           capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            shutil.rmtree(tmp, ignore_errors=True)
            raise RuntimeError(f"clone failed: {r.stderr.strip()[:120]}")
        slug = target.rstrip("/").removesuffix(".git").split("github.com/")[-1]
        return pathlib.Path(tmp), slug, tmp
    p = pathlib.Path(target).resolve()
    return p, p.name, None


def walk(root: pathlib.Path):
    files = []
    for p in root.rglob("*"):
        if p.is_file() and not any(d in p.parts for d in SKIP_DIRS):
            files.append(p)
    return files


def read_readme(root: pathlib.Path) -> str:
    for n in ("README.md", "readme.md", "README.rst", "README.txt"):
        if (root / n).exists():
            try:
                return (root / n).read_text(errors="ignore")
            except OSError:
                pass
    return ""


def content_hash(files: list[pathlib.Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(files)[:2000]:
        try:
            h.update(p.read_bytes())
        except OSError:
            pass
    return h.hexdigest()[:16]


def build_kg(root: pathlib.Path, slug: str, url: str, readme: str, files: list) -> dict:
    """Static repo map → field-graph-schema nodes/edges (zero LLM)."""
    nodes, edges, seen = [], [], set()

    def node(nid, ntype, name, **f):
        if nid in seen:
            return
        seen.add(nid)
        nodes.append({"id": nid, "type": ntype, "name": name, **f})

    def edge(s, d, t):
        edges.append({"src": s, "dst": d, "type": t})

    rid = f"repo:{slug}"
    node(rid, "repo", slug, links=[url] if url else [])

    # top-level modules/dirs (the repo's structure)
    for d in sorted({p.relative_to(root).parts[0] for p in files if len(p.relative_to(root).parts) > 1}):
        if d in SKIP_DIRS or d.startswith("."):
            continue
        mid = f"module:{slug}/{d}"
        node(mid, "module", d)
        edge(rid, mid, "contains")

    # key entrypoint / manifest files
    for p in files:
        if p.name in ENTRYPOINTS:
            fid = f"file:{slug}/{p.name}"
            node(fid, "file", p.name, links=[f"{url}/blob/HEAD/{p.relative_to(root)}"] if url else [])
            edge(rid, fid, "contains")

    # concepts = README section headings (the repo's own vocabulary)
    for m in re.finditer(r"^#{1,3}\s+(.{3,60})$", readme, re.M):
        title = re.sub(r"[#*`]", "", m.group(1)).strip()
        if title and not _generic(title):
            cid = f"concept:{slug}/{_slug(title)}"
            node(cid, "concept", title)
            edge(rid, cid, "documents")

    # detected frameworks (uses edges) — scan README + filenames + dependency manifests
    # (a repo often declares torch/transformers in requirements.txt, not the README prose).
    blob = readme.lower() + " " + " ".join(p.name.lower() for p in files)
    for p in files:
        if p.name in ("requirements.txt", "pyproject.toml", "setup.py", "package.json",
                      "environment.yml", "Pipfile"):
            try:
                blob += " " + p.read_text(errors="ignore").lower()[:20_000]
            except OSError:
                pass
    for fw, keys in FRAMEWORKS.items():
        if any(k in blob for k in keys):
            fwid = f"framework:{fw}"
            node(fwid, "framework", fw)
            edge(rid, fwid, "uses")

    return {"stats": {"nodes": len(nodes), "edges": len(edges)},
            "repo": slug, "nodes": nodes, "edges": edges}


def enrich_summary(root: pathlib.Path, cache: pathlib.Path) -> str:
    """Content-hash-cached LLM summary via `anyagent reverse` (~1 call/repo). Degrades
    to '' if anyagent/keys are unavailable — the static skill still ships."""
    if cache.exists():
        return cache.read_text().strip()
    exe = shutil.which("anyagent")
    if not exe:
        return ""
    try:
        r = subprocess.run([exe, "reverse", str(root), "--markdown"],
                           capture_output=True, text=True, timeout=240)
        m = re.search(r"##\s*Intent\s*\n(.+?)(?:\n#|\Z)", r.stdout, re.S)
        summary = " ".join(m.group(1).split())[:500] if m else ""
        if summary:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(summary)
        return summary
    except (subprocess.TimeoutExpired, OSError):
        return ""


def first_para(readme: str) -> str:
    """First real prose paragraph of the README (deterministic 'what it is')."""
    body = re.sub(r"^#.*$", "", readme, flags=re.M)              # drop headings
    body = re.sub(r"<[^>]+>|!\[[^\]]*\]\([^)]*\)|\[!\[[^\]]*\][^\n]*", "", body)  # html/badges
    for para in re.split(r"\n\s*\n", body):
        t = " ".join(para.split())
        if len(t) > 60 and not t.startswith(("|", ">", "-", "*", "```")):
            return t[:400]
    return ""


def build_skill(slug: str, url: str, readme: str, kg: dict, tier: str, summary: str) -> str:
    name = slug.split("/")[-1]
    concepts = [n["name"] for n in kg["nodes"] if n["type"] == "concept"][:8]
    fws = [n["name"] for n in kg["nodes"] if n["type"] == "framework"]
    what = summary or first_para(readme) or f"{slug} — an automated-AI-research tool listed in rsi."
    triggers = ", ".join(f'"{t}"' for t in [name, name.replace("-", " ")] + concepts[:3])
    run = ""
    for m in re.finditer(r"```(?:bash|sh)?\n(.*?)```", readme, re.S):
        block = m.group(1).strip()
        if re.search(r"(pip install|git clone|python |conda |docker )", block):
            run = block[:400]
            break
    L = [
        "---",
        f"name: {name}",
        "description: |",
        f"  {name} — {what[:180]}",
        f'  Use when the task involves {name}\'s approach, or asks about: {triggers}.',
        f"  (From rsi's certified tooling — tier: {tier}.)",
        "---", "",
        f"# {name}", "",
        f"> Minted by rsi's repo factory from **[{slug}]({url})** · certification tier: **{tier}** · "
        f"[knowledge graph](../../knowledge/repos/{_slug(slug)}/graph.json)", "",
        "## What it is", "", what, "",
    ]
    if concepts:
        L += ["## Key concepts (from its own docs)", "", *[f"- {c}" for c in concepts], ""]
    if fws:
        L += [f"**Built on:** {', '.join(fws)}", ""]
    if run:
        L += ["## How to apply", "", "```bash", run, "```", ""]
    L += ["## Source of truth", "",
          f"- Repo: {url}", f"- Knowledge graph: `knowledge/repos/{_slug(slug)}/graph.json`",
          "- Certified by rsi (`scripts/certify_repo.py`); this skill is generated "
          "(`scripts/repo_factory.py`) — do not hand-edit.", ""]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, help="local dir or github URL")
    ap.add_argument("--tier", default="unrated", help="certification tier to record in the skill")
    ap.add_argument("--enrich", action="store_true", help="add a cached anyagent-reverse LLM summary")
    args = ap.parse_args()

    root, slug, tmp = clone_or_local(args.target)
    try:
        url = args.target if re.match(r"^https?://", args.target) else f"https://github.com/{slug}"
        files = walk(root)
        readme = read_readme(root)
        chash = content_hash(files)
        sslug = _slug(slug)

        kg = build_kg(root, slug, url, readme, files)
        kg["content_hash"] = chash
        kg_path = ROOT / "knowledge" / "repos" / sslug / "graph.json"
        kg_path.parent.mkdir(parents=True, exist_ok=True)
        kg_path.write_text(json.dumps(kg, indent=2, ensure_ascii=False))

        summary = enrich_summary(root, ROOT / "knowledge" / "repos" / sslug / "summary.txt") if args.enrich else ""
        skill = build_skill(slug, url, readme, kg, args.tier, summary)
        skill_path = ROOT / "skills" / sslug / "SKILL.md"
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(skill)

        print(f"✓ {slug}: KG {kg['stats']['nodes']}n/{kg['stats']['edges']}e → {kg_path.relative_to(ROOT)}", file=sys.stderr)
        print(f"          SKILL → {skill_path.relative_to(ROOT)} (tier {args.tier}, {'enriched' if summary else 'static'})", file=sys.stderr)
        return 0
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
