# Changelog

All notable changes to this repo are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **Repo→{KG, skill} factory + backbone registry** — rsi is now the hub of 1) knowledge
  2) tooling 3) experts. For each Certified/Verified repo, `scripts/repo_factory.py` mints
  (static, zero-LLM core; `--enrich` adds a content-hash-cached `anyagent reverse` summary):
  a **knowledge graph** (`knowledge/repos/<slug>/graph.json`, field-graph schema so
  `docs/index.html` renders it) and an **agentic skill** (`skills/<slug>/SKILL.md` — the
  frontmatter `description` is the progressive-disclosure trigger; body = what-it-does ·
  how-to-apply · links to KG+repo). `scripts/build_repo_tools.py` orchestrates the set and
  emits the **backbone registry** (`skills/registry.json` + `skills/README.md`) that `/rsi`
  loads always-on, while each skill body loads on-demand. **19 toolsets minted** from the
  Verified set. Fast/cheap (static + hash-cached), up-to-date (re-mint only on content-hash
  change), future-proof (pure data artifacts + portable skills), quality-gated (only
  Certified/Verified repos; distinctive-vocabulary triggers, boilerplate stoplisted).
  `make repo-tools` regenerates; `make check` drift-gates `skills/registry.json`.
- **AI-native self-audit** — `data/ainative.yml` encodes the loop-engineering /
  physical-ai-native principles (loops-not-oneshot · independent-referee · no-evidence⇒No ·
  regression-gated · spec-as-data · agent-native · compounding-memory · human-gated ·
  verify-live), each backed by *real evidence* (a file that must exist or a regex that must
  be found). `scripts/ainative.py --gate 85` scores rsi's own operation (currently **100/100**,
  all evidence verified) and is wired into `make check`, so a regression in *how* the repo
  operates also fails CI.
- **Frontier Radar (live tracker)** — `scripts/track.py` refreshes recent works + repo
  activity for the people & repos rsi follows via **open arXiv/GitHub APIs** into a generated
  `knowledge/_frontier.yml` (no-evidence ⇒ "none found", never fabricated). `build_readme.py`
  renders a 🛰️ Frontier Radar section from it (newest-first), and a weekly **`track.yml`**
  Action opens a human-gated "what moved" PR. (Verified live: surfaced Clune's *"Towards
  End-to-End Automation of AI Research"* + live repo stars.) The researchers↔labs↔papers
  **field graph** is already served by the interactive map (`docs/index.html`); a dedicated
  bi-temporal (time-sliced) view is a documented fast-follow.
- **RSI-Certified rubric (deep, per-repo, rubric-as-data)** — `data/certify.yml` is the
  single source of truth; `scripts/certify_repo.py --target <dir|github-url> --gate N`
  scores an AI-Scientist-style repo on **safety · reproducibility · relevance · autonomy ·
  eval-with-teeth · provenance · docs · cross-runtime**, weighting only MEASURED dimensions
  (no-evidence ⇒ excluded, never a fake pass), with **blocking gates** (safety, relevance)
  that can't pass on unmeasured items, and `--gate` exits non-zero to gate CI. STATIC ONLY —
  it never runs the target (executing a self-modifying research agent to "prove" it is the
  risk, not the proof); it flags model-generated-code execution and requires a maker≠checker
  signal. Emits a shields badge; a composite action **[`.github/actions/rsi-certify`](.github/actions/rsi-certify/action.yml)**
  lets any tool author self-certify in their own CI. Dogfooded: **SakanaAI/AI-Scientist →
  ✅ Certified 90/100**, **ShengranHu/ADAS → 🟡 Provisional 73/100** (gaps: reproducibility,
  autonomy, eval). Complementary to `scripts/certify.py` (the fast signals roll-up across the
  listed registry).
- **Spec-as-data foundation** (porting the FM-os / longevity-loop architecture): every
  entry now lives in `data/*.yml` (`papers`, `tools`, `people`, `labs`, `benchmarks`,
  `talks`), bootstrapped losslessly from `knowledge/graph.json` via
  `scripts/graph_to_data.py`; prose sections captured verbatim in `data/prose/*.md`.
  `scripts/validate.py` schema-gates every entry (required fields + http(s) URL +
  identity-dedup) and is wired into `make check`; `lychee.toml` configures the CI link
  check.
- **Generated, drift-gated README** — the README is now a build artifact:
  `scripts/build_readme.py` renders it from `data/*.yml` + verbatim `data/prose/*.md`,
  and `make check` runs `build_readme.py --check` so CI fails if the committed README ≠
  the generated one (the "living" claim is now enforced, not aspirational). The graph
  coupling is preserved — `data → build_readme → README → awesome_kg → graph` reproduces
  **139 nodes** exactly (edges 246→244, a correct de-dup of two double-listed benchmarks);
  Papers/Tools/Benchmarks are generated as awesome_kg-compatible tables, People/Talks/
  narrative stay verbatim prose. `make build` regenerates README + graph + map together;
  the `knowledge` workflow now builds from `data/`, and a new `ci.yml` runs the drift gate
  + lychee on every PR. The 🏅 Certified Tooling summary is now owned by the generator
  (dateless, so it can't drift daily).
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
  `--gate` exits non-zero for CI. Summary folded into the README; full table in
  [`docs/CERTIFIED.md`](docs/CERTIFIED.md); raw data in `knowledge/certifications.json`.
  Covers four tooling kinds via one shared schema: repos, **agent-skills** (SKILL.md,
  `skills_sync.py`), **MCP servers** (`mcp_sync.py`), and **workflows** (`workflows_sync.py`).
- **🥇 gold tier** (`scripts/certify_gold.py`) — fills the two blocking dims the signals
  tier leaves unmeasured: `works` via a `anyagent analyze` STATIC read of a shallow clone
  (never runs the code), and `safe` via a static safety scan (committed-secret patterns,
  `curl | sh`, `shell=True`, `rm -rf ~`). Re-tiers to 🥇 only when both pass — e.g. it
  flagged that `jennyzzt/dgm` executes self-modified code (safe=20), correctly withholding
  the badge. Honest by construction: still 0 🥇 until a tool clears every bar.
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
