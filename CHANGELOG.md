# Changelog

All notable changes to this repo are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **Weekly auto-sync pipeline** — the repo now keeps *itself* fresh. Source adapters
  (`scripts/ingest/`) fetch candidates from live primary sources — `github_sync.py`
  (refresh stale star counts + discover new repos; found 18/29 listed repos stale, e.g.
  MetaGPT ~48k→69k, dspy ~22k→36k), `arxiv_sync.py` (fresh RSI papers), and
  `skills_sync.py` (RSI agent-skills / SKILL.md repos). `groundbreakers.py` ranks them
  into a weekly **RSI Groundbreakers** slate (Seminal · Industrial Impact · Social Good ·
  Best Explainer · Golden Meme; no-evidence ⇒ "no award"). `.github/workflows/ingest.yml`
  runs it weekly and opens ONE review PR — nothing lands in the README until a human merges.
- **🏅 Certified Tooling** — an evidence-backed tier for every tool, the trust layer
  [skills.sh](https://www.skills.sh/) (install-count-only) lacks. `scripts/certify.py`
  scores curated repos + discovered skills across a data-driven rubric
  (relevant/maintained/adopted/works/safe) into 🥉 Listed → 🥈 Verified → 🥇 RSI-Certified.
  The aggregate is computed in code, unmeasured dimensions can't fake a pass, and
  `--gate` exits non-zero for CI. 🥇 requires *works*+*safe* via `anyagent analyze`/`brace`
  (not yet run, so honestly 0 🥇). Summary folded into the README; full table in
  [`docs/CERTIFIED.md`](docs/CERTIFIED.md); raw data in `knowledge/certifications.json`.
- **`make check` finish line + test suite** — `tests/test_pipeline.py` (19 stdlib
  unittest cases) pins every pure function the weekly run relies on, wired into
  `make check` (tests + candidate validation + graph-compile). This closes the *code*
  loop, not just the data loop — a regression is caught before a PR opens. `anyagent
  analyze` quality: 50 → 58.
- **"✨ Ask the field"** on the interactive map: grounded Q&A over the knowledge graph,
  answered by frontier models on **NVIDIA's free NIM API** (GLM 5.1 / DeepSeek v4 /
  Kimi K2.6). Visitors bring their own free key (build.nvidia.com/models, ~40 req/min);
  it lives only in their browser's localStorage and reaches NVIDIA via a keyless CORS
  bridge (nim-bridge.vercel.app — needed because NVIDIA's API only allows CORS from
  build.nvidia.com). Answers cite graph nodes as clickable chips that select them on
  the map. Retrieval is client-side over `knowledge/graph.json` — no backend, no
  tracking, the page stays a static file.
- **Living knowledge graph**: the README's tables now compile into a typed graph
  (`knowledge/graph.json`, 139 nodes · 246 edges: papers/repos/people/labs/talks/benchmarks
  with `authored_by`/`has_code`/`member_of`/`part_of`/`builds_on` edges) plus a
  self-contained interactive map at `docs/index.html` (GitHub Pages-ready) — so readers
  can interrogate the field, not just scroll it.
- `knowledge/enrichments.json` — curator-written lineage edges (Gödel Machine → AI-GAs →
  DGM, FunSearch → AlphaEvolve, …) that survive every regeneration.
- `scripts/awesome_kg.py` — deterministic, stdlib-only README→graph compiler (vendored
  from the [sos `living-repo` skill](https://github.com/wjlgatech/sos)); zero LLM calls,
  CI-safe, never invents a node.
- `scripts/check_freshness.py` + `.github/workflows/freshness.yml` — weekly link check
  that opens an issue on dead links. The README has claimed "automated weekly freshness
  checks via GitHub Actions" since day one; **this makes the claim true.**
- `.github/workflows/knowledge.yml` — recompiles graph + map on every README merge, so
  contributors only ever edit the README.

### Fixed
- 5 dead links found by the first freshness run: the ACL placeholder URL
  (`acl-long.xxx`) and the Springer DOI now point to their verified arXiv pages
  (2505.13259, 2110.05242); AgentRxiv code → agentrxiv.github.io;
  richard.socher.org → www.socher.org; ICLR 2025 keynote → iclr.cc/virtual/2025.

### Investigated / Rejected
- **LLM-extracted graph via dreammaketrue `kgfy`**: with the engine on its local
  qwen2.5:7b backup it produced 53 thin nodes and 25 edges, including hallucinated
  content ("Karpathy alchemy quote" — Karpathy appears nowhere in this README), vs the
  deterministic compiler's 139 fully-traceable nodes and 246 edges. Rejected until the
  engine runs a frontier model; the deterministic parse is also the only approach that
  can run in CI on every merge.
