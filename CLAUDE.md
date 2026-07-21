# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

**rsi** ("Awesome Automated AI Research") is a *spec-as-data* living knowledge repo: curated data about the Recursive Self-Improvement / automated-AI-research field (papers, tools, people, labs, benchmarks) that **compiles** into a README, a typed knowledge graph, an interactive map, and a set of agentic skills. The Python pipeline is stdlib-only + PyYAML — no other dependencies.

## The one rule that matters

**NEVER hand-edit `README.md`, `skills/registry.json`, `skills/README.md`, or `docs/CERTIFIED.md` — they are generated.** The source of truth is `data/*.yml` (tables) + `data/prose/*.md` (prose fragments). Edit those, then run `make build`. CI drift-gates the README (`build_readme.py --check`) and the skills registry, so a hand-edit fails `make check`.

## Commands

```bash
make check        # THE finish line — what CI runs: validate + tests + README drift gate
                  #   + AI-native audit (gate 85) + registry drift gate + ingest check
make build        # data/*.yml → README.md → knowledge/graph.json + docs/index.html
make graph        # recompile only the knowledge graph + interactive map from README
make validate     # schema-gate data/*.yml (required fields + URLs)
make ainative     # self-audit against loop-engineering principles (scripts/ainative.py --gate 85)
make repo-tools   # re-mint {KG, skill} per Certified/Verified repo + rebuild skills/registry.json
make certify      # signals roll-up across the registry → docs/CERTIFIED.md + README
make certify-repo TARGET=<dir|github-url> [GATE=75]   # deep RSI-Certified rubric on one repo
make ingest       # run all source adapters (github/arxiv/skills/mcp/workflows) → candidates
make sync         # full weekly run: ingest → rank → certify → check → web pack
make freshness    # probe every README link

# Tests (stdlib unittest, no pytest)
python3 -m unittest discover -s tests
python3 -m unittest tests.test_pipeline.TestGithubSync            # one class
python3 -m unittest tests.test_pipeline.TestGithubSync.test_name  # one test
```

Requires `pip install pyyaml` (the only dependency; CI uses Python 3.12).

## Architecture — the data flow

```
data/*.yml + data/prose/*.md
   └─ scripts/build_readme.py ──→ README.md          (generated, drift-gated)
         └─ scripts/awesome_kg.py ──→ knowledge/graph.json + docs/index.html
                                       (+ knowledge/enrichments.json survives regeneration)
```

- `scripts/rsidata.py` — shared helpers (data paths, YAML loader, md escaping) used by all pipeline scripts.
- `scripts/awesome_kg.py` parses the *generated README* (tables → typed nodes/edges), so the graph always reflects the data. Deterministic, zero LLM calls.
- `knowledge/enrichments.json` holds curator-written lineage edges that must survive regeneration — add relationships there, not in the graph output.

### Ingest → certify loop (weekly automation)

`scripts/ingest/*.py` adapters (github, arxiv, skills, mcp, workflows) emit `knowledge/candidates.*.json` → `scripts/groundbreakers.py` ranks/merges them → `scripts/certify.py` assigns evidence-backed tiers (🥇 Certified / 🥈 Verified / 🥉 Listed) into `knowledge/certifications.json`. GitHub Actions (`.github/workflows/`): `ci.yml` runs `make check` + lychee link check; `knowledge.yml` recompiles the graph on merge; `freshness.yml`, `ingest.yml`, `track.yml` open human-gated PRs weekly. All findings are evidence-backed — **no evidence ⇒ no badge / "none found", never fabricated**.

### Repo→{KG, skill} factory

`scripts/repo_factory.py` (orchestrated by `scripts/build_repo_tools.py`) mints, for each Certified/Verified repo: a knowledge graph at `knowledge/repos/<slug>/graph.json` and an agentic skill at `skills/<slug>/SKILL.md`. `skills/registry.json` is the always-on backbone index; skill bodies load on-demand (progressive disclosure). Static + content-hash-cached — re-mints only when the source repo changed.

### Deep certification (`scripts/certify_repo.py`)

Rubric lives in `data/certify.yml` (rubric-as-data). STATIC ANALYSIS ONLY — it must never execute the target repo (running a self-modifying research agent to "prove" it is the risk, not the proof). Unmeasured dimensions are excluded from the score, never counted as passes.

## Sub-projects

- **`web/`** — **gitignored, local-only** (a personal agentic-portfolio fork containing personal data; never commit it to this public repo — see `.gitignore`). It has its own `CLAUDE.md` and `AGENTS.md` with binding rules; read those before touching anything under `web/`. Commands run from `web/`: `npm run dev`, `npm run build` (the real gate), `npm test`. `node web/scripts/gen-rsi-instance.mjs` (or `make web-pack`) regenerates its data pack from `knowledge/graph.json`.
- **`openspace-trial/`** — evaluation scaffold for HKUDS/OpenSpace. Note its RUNBOOK warning: install from source, **not** `pip install openspace` (that PyPI name is an unrelated package).

## Conventions

- Tests are stdlib `unittest` only — keep the zero-dependency ethos; every pure function a weekly run relies on gets pinned in `tests/test_pipeline.py`.
- `data/ainative.yml` encodes the repo's operating principles, each backed by real evidence (a file or regex that must exist); `scripts/ainative.py` scores compliance and fails CI below 85 — if you change *how* the repo operates, update the evidence there.
- New papers/tools/people go into the matching `data/*.yml` following existing entry shapes; `make validate` enforces required fields and URLs.
