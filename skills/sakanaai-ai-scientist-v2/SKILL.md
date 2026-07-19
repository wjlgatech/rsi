---
name: AI-Scientist-v2
description: |
  AI-Scientist-v2 — The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search
  Use when the task involves AI-Scientist-v2's approach, or asks about: "AI-Scientist-v2", "AI Scientist v2", "Set AWS credentials if using Bedrock", "export AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"", "export AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_KEY"".
  (From rsi's certified tooling — tier: 🥈 Verified.)
---

# AI-Scientist-v2

> Minted by rsi's repo factory from **[SakanaAI/AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2)** · certification tier: **🥈 Verified** · [knowledge graph](../../knowledge/repos/sakanaai-ai-scientist-v2/graph.json)

## What it is

The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search

## Key concepts (from its own docs)

- Set AWS credentials if using Bedrock
- export AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
- export AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_KEY"
- export AWS_REGION_NAME="your-aws-region"
- Generate Research Ideas
- Run AI Scientist-v2 Paper Generation Experiments
- Citing The AI Scientist-v2
- Frequently Asked Questions

**Built on:** pytorch, transformers, openai, anthropic

## How to apply

```bash
# Create a new conda environment
conda create -n ai_scientist python=3.11
conda activate ai_scientist

# Install PyTorch with CUDA support (adjust pytorch-cuda version for your setup)
conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia

# Install PDF and LaTeX tools
conda install anaconda::poppler
conda install conda-forge::chktex

# Install Python package requireme
```

## Source of truth

- Repo: https://github.com/SakanaAI/AI-Scientist-v2
- Knowledge graph: `knowledge/repos/sakanaai-ai-scientist-v2/graph.json`
- Certified by rsi (`scripts/certify_repo.py`); this skill is generated (`scripts/repo_factory.py`) — do not hand-edit.
