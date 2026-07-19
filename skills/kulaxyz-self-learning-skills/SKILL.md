---
name: self-learning-skills
description: |
  self-learning-skills — Every session you do hard debugging or rediscover the same thing — *how do I reach the prod DB? where do the creds live? what's the deploy command? how do I verify this live?* — an
  Use when the task involves self-learning-skills's approach, or asks about: "self-learning-skills", "self learning skills", "self-learning-skills", "The loop (same everywhere)", "npx — recommended (works with 70+ agents)".
  (From rsi's certified tooling — tier: 🥈 Verified.)
---

# self-learning-skills

> Minted by rsi's repo factory from **[Kulaxyz/self-learning-skills](https://github.com/Kulaxyz/self-learning-skills)** · certification tier: **🥈 Verified** · [knowledge graph](../../knowledge/repos/kulaxyz-self-learning-skills/graph.json)

## What it is

Every session you do hard debugging or rediscover the same thing — *how do I reach the prod DB? where do the creds live? what's the deploy command? how do I verify this live?* — and that hard-won knowledge evaporates when the session ends. The next session starts from zero and re-learns it.

## Key concepts (from its own docs)

- self-learning-skills
- The loop (same everywhere)
- npx — recommended (works with 70+ agents)
- Claude Code plugin
- Manual
- Any AGENTS.md agent (Codex, Zed, Aider, Gemini CLI, …)
- Triage: skill, memory, or skip?
- Promotion rule (don't enshrine guesses)

**Built on:** mcp

## How to apply

```bash
git clone https://github.com/kulaxyz/self-learning-skills

# Claude Code — global (or into a project's .claude/skills/ to share via git)
cp -R self-learning-skills/skills/self-learning ~/.claude/skills/

# Cursor — auto-loads .cursor/rules/ (harvested rules land in .cursor/rules/learned/)
mkdir -p .cursor/rules
cp self-learning-skills/.cursor/rules/self-learning.mdc .cursor/rules/

# Any AGENTS.md
```

## Source of truth

- Repo: https://github.com/Kulaxyz/self-learning-skills
- Knowledge graph: `knowledge/repos/kulaxyz-self-learning-skills/graph.json`
- Certified by rsi (`scripts/certify_repo.py`); this skill is generated (`scripts/repo_factory.py`) — do not hand-edit.
