---
name: mle-bench
description: |
  mle-bench — Code for the paper ["MLE-Bench: Evaluating Machine Learning Agents on Machine Learning Engineering"](https://arxiv.org/abs/2410.07095). We have released the code used to construct 
  Use when the task involves mle-bench's approach, or asks about: "mle-bench", "mle bench", "MLE-bench", "Leaderboard", "Additional Leaderboard Submissions".
  (From rsi's certified tooling — tier: 🥈 Verified.)
---

# mle-bench

> Minted by rsi's repo factory from **[openai/mle-bench](https://github.com/openai/mle-bench)** · certification tier: **🥈 Verified** · [knowledge graph](../../knowledge/repos/openai-mle-bench/graph.json)

## What it is

Code for the paper ["MLE-Bench: Evaluating Machine Learning Agents on Machine Learning Engineering"](https://arxiv.org/abs/2410.07095). We have released the code used to construct the dataset, the evaluation logic, as well as the agents we evaluated for this benchmark.

## Key concepts (from its own docs)

- MLE-bench
- Leaderboard
- Additional Leaderboard Submissions
- Producing Scores for the Leaderboard
- Benchmarking
- Lite Evaluation
- Pre-Commit Hooks (Optional)
- Dataset

**Built on:** pytorch, tensorflow, jax, transformers, langchain, openai, anthropic, gymnasium

## How to apply

```bash
uv run python experiments/aggregate_grading_reports.py --experiment-id <exp_id> --split low
uv run python experiments/aggregate_grading_reports.py --experiment-id <exp_id> --split medium
uv run python experiments/aggregate_grading_reports.py --experiment-id <exp_id> --split high
uv run python experiments/aggregate_grading_reports.py --experiment-id <exp_id> --split split75
```

## Source of truth

- Repo: https://github.com/openai/mle-bench
- Knowledge graph: `knowledge/repos/openai-mle-bench/graph.json`
- Certified by rsi (`scripts/certify_repo.py`); this skill is generated (`scripts/repo_factory.py`) — do not hand-edit.
