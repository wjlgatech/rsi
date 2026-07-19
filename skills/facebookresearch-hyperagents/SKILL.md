---
name: HyperAgents
description: |
  HyperAgents — Self-referential self-improving agents that can optimize for any computable task
  Use when the task involves HyperAgents's approach, or asks about: "HyperAgents", "HyperAgents", "To build the docker container", "Running HyperAgents", "See the script for args, and baseline selections".
  (From rsi's certified tooling — tier: 🥈 Verified.)
---

# HyperAgents

> Minted by rsi's repo factory from **[facebookresearch/HyperAgents](https://github.com/facebookresearch/HyperAgents)** · certification tier: **🥈 Verified** · [knowledge graph](../../knowledge/repos/facebookresearch-hyperagents/graph.json)

## What it is

Self-referential self-improving agents that can optimize for any computable task

## Key concepts (from its own docs)

- To build the docker container
- Running HyperAgents
- See the script for args, and baseline selections
- File Structure
- Logs from Experiments
- Safety Consideration
- Citing

**Built on:** pytorch, openai, anthropic, gymnasium

## How to apply

```bash
# Create virtual environment
python3.12 -m venv venv_nat
source venv_nat/bin/activate
pip install -r requirements.txt
pip install -r requirements_dev.txt
# To build the docker container
docker build --network=host -t hyperagents .
```

## Source of truth

- Repo: https://github.com/facebookresearch/HyperAgents
- Knowledge graph: `knowledge/repos/facebookresearch-hyperagents/graph.json`
- Certified by rsi (`scripts/certify_repo.py`); this skill is generated (`scripts/repo_factory.py`) — do not hand-edit.
