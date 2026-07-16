# RSI — the living, auto-syncing "one place for all things RSI".
# `make check` is the pipeline's finish line (what `anyagent goal` looks for).

.PHONY: check graph freshness ingest sync

check:  ## validate data + run tests + verify candidates + README still compiles to a graph
	python3 scripts/validate.py
	python3 -m unittest discover -s tests
	python3 scripts/check_ingest.py --readme README.md --candidates knowledge/candidates.json

validate:  ## schema-gate data/*.yml (required fields + URLs)
	python3 scripts/validate.py

data-bootstrap:  ## one-time: seed data/*.yml from knowledge/graph.json
	python3 scripts/graph_to_data.py

graph:  ## recompile the knowledge graph + interactive map from the README
	python3 scripts/awesome_kg.py build README.md \
		--out knowledge/graph.json --html docs/index.html \
		--enrich knowledge/enrichments.json --title "Awesome Automated AI Research"

freshness:  ## probe every README link
	python3 scripts/check_freshness.py README.md

# Run every source adapter, then rank into a weekly PR body + merged candidates.
# GITHUB_TOKEN lifts the API rate limit (Actions provides it free).
ingest:  ## fetch candidates from every source adapter (repos, papers, skills, MCP, workflows)
	python3 scripts/ingest/github_sync.py    --readme README.md --out knowledge/candidates.github.json    --min-stars 300
	python3 scripts/ingest/arxiv_sync.py     --readme README.md --out knowledge/candidates.arxiv.json     --days 14
	python3 scripts/ingest/skills_sync.py    --readme README.md --out knowledge/candidates.skills.json    --min-stars 20
	python3 scripts/ingest/mcp_sync.py       --readme README.md --out knowledge/candidates.mcp.json       --min-stars 20
	python3 scripts/ingest/workflows_sync.py --readme README.md --out knowledge/candidates.workflows.json --min-stars 30

certify:  ## certify tooling (repos + skills + MCP + workflows) -> badges in README + docs
	python3 scripts/certify.py --markdown docs/CERTIFIED.md --inject README.md

gold:  ## 🥇 deep-certify the top Verified tools (clone + anyagent analyze + safety scan)
	python3 scripts/certify_gold.py --top 5 --markdown docs/CERTIFIED.md --inject README.md

sync: ingest  ## full weekly run: ingest -> rank -> certify -> validate -> refresh web pack
	python3 scripts/groundbreakers.py --glob "knowledge/candidates.*.json" \
		--pr-body /tmp/rsi_pr_body.md --out knowledge/candidates.json
	$(MAKE) certify
	$(MAKE) check
	@# Loop closure: regenerate the agentic web app's data pack from the fresh graph.
	@node web/scripts/gen-rsi-instance.mjs 2>/dev/null || echo "  (skip web pack regen — node or web/ unavailable)"

web-pack:  ## regenerate the agentic web app's RSI instance pack from the knowledge graph
	node web/scripts/gen-rsi-instance.mjs
