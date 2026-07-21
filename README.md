# 🤖 Recursive Self Improvement (RSI)

<div align="center">

[![Awesome](https://awesome.re/badge-flat2.svg)](https://awesome.re)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Last Updated](https://img.shields.io/github/last-commit/wjlgatech/rsi-os?style=flat-square&label=last%20updated)](https://github.com/wjlgatech/rsi-os/commits/main)
[![Stars](https://img.shields.io/github/stars/wjlgatech/rsi-os?style=flat-square)](https://github.com/wjlgatech/rsi-os/stargazers)
[![Contributors](https://img.shields.io/github/contributors/wjlgatech/rsi-os?style=flat-square)](https://github.com/wjlgatech/rsi-os/graphs/contributors)

**The most comprehensive, community-driven, living resource on Automated AI Research.**

*From the Gödel Machine (2003) to AI Scientists publishing in Nature (2026) — everything you need to understand, build, and contribute to the era of self-improving AI.*

[Papers](#-papers) • [Tools & Repos](#-open-source-tools--repos) • [People & Labs](#-people--labs-to-follow) • [Talks & Interviews](#-talks-interviews--podcasts) • [Benchmarks](#-benchmarks--leaderboards) • [Roadmap](#-learning-roadmaps) • [Contribute](#-how-to-contribute)

</div>

---

> **⚡ What makes this repo different from every other list?**
> 1. **Recursive Lab–focused** — the only list featuring all **8 co-founders**: Jeff Clune, Tim Rocktäschel, Richard Socher, Caiming Xiong, **Yuandong Tian**, Tim Shi, Mingchen Zhuge & Yingbo Zhou — with full publication graphs
> 2. **Competitive analysis baked in** — citation counts, reproducibility status, and impact scores for every paper
> 3. **Dual roadmaps** — one for absolute beginners, one for frontier researchers
> 4. **Community-updated** — automated weekly freshness checks via GitHub Actions
> 5. **Cross-linked** — papers → code → talks → people → labs, all connected

---

🔁 **Part of a build-in-public flywheel** → **[FM-os](https://github.com/wjlgatech/FM-os)** (the spec-as-data method this repo runs on) · **[longevity-loop](https://github.com/wjlgatech/longevity-loop)** (the same method, applied to aging science).

---

## 📚 Table of Contents

- [🕸️ Living Knowledge Graph](#-living-knowledge-graph)
- [🏛️ Field Overview & Taxonomy](#-field-overview--taxonomy)
- [📄 Papers](#-papers)
  - [🧬 Foundational & Visionary](#-foundational--visionary)
  - [🔬 Automated Scientific Discovery](#-automated-scientific-discovery)
  - [🤖 Automated Agentic System Design](#-automated-agentic-system-design)
  - [🧠 Meta-Learning & Self-Improvement](#-meta-learning--self-improvement)
  - [🌐 Open-Ended Learning & Curriculum](#-open-ended-learning--curriculum)
  - [✏️ Prompt, Reward & Code Automation](#-prompt-reward--code-automation)
  - [📊 Benchmarks & Evaluation](#-benchmarks--evaluation)
  - [🗺️ Surveys & Position Papers](#-surveys--position-papers)
- [🛠️ Open-Source Tools & Repos](#-open-source-tools--repos)
- [👥 People & Labs to Follow](#-people--labs-to-follow)
  - [🎯 Recursive Lab Members](#-recursive-lab-members)
  - [🔬 Affiliated Researchers](#-affiliated-researchers)
  - [🏢 Key Labs](#-key-labs)
- [🎙️ Talks, Interviews & Podcasts](#-talks-interviews--podcasts)
- [📈 Benchmarks & Leaderboards](#-benchmarks--leaderboards)
- [📅 Timeline: Key Milestones](#-timeline-key-milestones)
- [🗺️ Learning Roadmaps](#-learning-roadmaps)
  - [Beginner Path (0–3 months)](#beginner-path-03-months)
  - [Advanced Researcher Path](#advanced-researcher-path)
- [🏆 Competitive Landscape Analysis](#-competitive-landscape-analysis)
- [🤝 How to Contribute](#-how-to-contribute)
- [📜 Citation](#-citation)

---

## 🕸️ Living Knowledge Graph

This list is not just tables — it **compiles**. Every paper, repo, person, lab, talk and benchmark below is a node in a typed knowledge graph, with `authored_by` / `has_code` / `member_of` / `builds_on` edges connecting them:

- **🗺️ [Explore the interactive map](https://wjlgatech.github.io/rsi/)** — force-layout graph with search, type filters, and click-to-inspect (self-contained HTML; also works locally: open [`docs/index.html`](docs/index.html))
- **✨ Ask the field** — hit the *Ask* button on the map for grounded Q&A: a frontier model (GLM 5.1 / DeepSeek v4 / Kimi K2.6 on **NVIDIA's free API**) answers from the graph and cites nodes as clickable chips. Bring your own free key from [build.nvidia.com/models](https://build.nvidia.com/models) — it stays in your browser
- **🧩 [`knowledge/graph.json`](knowledge/graph.json)** — the full machine-readable graph (139 nodes · 246 edges) for your own agents, RAG pipelines, or analysis
- **🧬 [`knowledge/enrichments.json`](knowledge/enrichments.json)** — curator-written lineage edges (Gödel Machine → AI-GAs → DGM …) that survive regeneration

**It stays alive automatically.** Editing the README is all a contributor ever does — on every merge, [a GitHub Action](.github/workflows/knowledge.yml) recompiles the graph and the map, and [a weekly freshness check](.github/workflows/freshness.yml) probes every link and opens an issue if any die.

```bash
# regenerate locally (stdlib-only, deterministic, zero LLM calls)
python3 scripts/awesome_kg.py build README.md \
  --out knowledge/graph.json --html docs/index.html \
  --enrich knowledge/enrichments.json --title "Awesome Automated AI Research"

# check every link is still alive
python3 scripts/check_freshness.py README.md
```

> Built with the [`living-repo`](https://github.com/wjlgatech/sos/tree/main/plugins/sos/skills/living-repo) skill from the [sos toolkit](https://github.com/wjlgatech/sos) — point it at any awesome-list to get the same treatment.

---

## 🏛️ Field Overview & Taxonomy

**Automated AI Research** = using AI systems to accelerate or replace steps in the AI research pipeline. The field has 6 converging tracks:

```
┌─────────────────────────────────────────────────────────────┐
│              AUTOMATED AI RESEARCH TAXONOMY                 │
├─────────────────────────────────────────────────────────────┤
│ 1. SELF-IMPROVING AGENTS   Gödel Machine → AI-GAs → DGM    │
│ 2. AUTOMATED SCIENCE       AI Scientist → Co-Scientist      │
│ 3. AGENTIC SYSTEM DESIGN   ADAS → GPTSwarm → MetaGPT        │
│ 4. OPEN-ENDED LEARNING     POET → PLR → OMNI-EPIC            │
│ 5. CODE/REWARD/PROMPT AUTO Eureka → PromptBreeder → OPRO    │
│ 6. ML ENGINEERING AGENTS   MLE-Bench → SWE-bench → MLGym    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📄 Papers

> 📌 Format: **Title** — Authors (Affiliation) — Venue Year | ⭐ Citations | 💻 Code

### Foundational & Visionary

| Paper | Authors | Venue | Year | Citations | Code |
|-------|---------|-------|------|-----------|------|
| [**Gödel Machines: Self-Referential Universal Problem Solvers**](https://arxiv.org/abs/cs/0309048) | Jürgen Schmidhuber | arXiv | 2003 | ~77 | — |
| [**AI-Generating Algorithms (AI-GAs)**](https://arxiv.org/abs/1905.10985) | Jeff Clune (UBC / **Recursive**) | arXiv | 2019 | ~201 | — |
| [**Open-Endedness is Essential for Artificial Superhuman Intelligence**](https://arxiv.org/abs/2406.04268) | Hughes, Dennis, Parker-Holder, Rocktäschel et al. (DeepMind) | ICML Oral | 2024 | ~111 | — |
| [**Why I Work on Self-Improving AI Despite the Risks**](https://jeffclune.com) | Jeff Clune (**Recursive**) | Blog | 2024 | — | — |

### Automated Scientific Discovery

| Paper | Authors | Venue | Year | Citations | Code |
|-------|---------|-------|------|-----------|------|
| [**The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery**](https://arxiv.org/abs/2408.06292) | C. Lu, C. Lu, Lange, Foerster, **Clune**, Ha, **S. Hu** et al. (Sakana AI / UBC) | Nature | 2024→2026 | ~1027 | [💻](https://github.com/SakanaAI/AI-Scientist) |
| [**The AI Scientist-v2: Workshop-Level Automated Scientific Discovery**](https://arxiv.org/abs/2504.08066) | Yamada*, Lange*, C. Lu*, **S. Hu**, C. Lu, Foerster, **Clune**†, Ha† (Sakana AI / UBC) | arXiv | 2025 | ~330 | [💻](https://github.com/SakanaAI/AI-Scientist-v2) |
| [**Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents**](https://arxiv.org/abs/2505.22954) | Zhang*, **S. Hu***, C. Lu, Lange†, **Clune**† (UBC / Sakana AI) | ICLR | 2026 | ~138 | [💻](https://github.com/jennyzzt/dgm) |
| [**Towards an AI Co-Scientist**](https://arxiv.org/abs/2502.18864) | Gottweis, Weng, Daryin, Tu, Palepu et al. (Google DeepMind) | arXiv | 2025 | ~533 | — |
| [**AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery**](https://arxiv.org/abs/2506.01882) | Novikov, Vũ, Eisenberger et al. (Google DeepMind) | arXiv | 2025 | ~696 | — |
| [**FunSearch: Mathematical Discoveries from Program Search with LLMs**](https://www.nature.com/articles/s41586-023-06924-6) | Romera-Paredes, Barekatain, Novikov, Balog et al. (Google DeepMind) | Nature | 2024 | ~1482 | [💻](https://github.com/google-deepmind/funsearch) |
| [**Agent Laboratory: Using LLM Agents as Research Assistants**](https://arxiv.org/abs/2501.04227) | Schmidgall, Su, Wang et al. | ACL Findings | 2025 | ~378 | [💻](https://github.com/SamuelSchmidgall/AgentLaboratory) |
| [**AgentRxiv: Towards Collaborative Autonomous Research**](https://arxiv.org/abs/2503.18102) | Schmidgall, Moor | arXiv | 2025 | ~62 | — |

### Automated Agentic System Design

| Paper | Authors | Venue | Year | Citations | Code |
|-------|---------|-------|------|-----------|------|
| [**Automated Design of Agentic Systems (ADAS)**](https://arxiv.org/abs/2408.08435) | **S. Hu**, C. Lu, **J. Clune** (UBC / **Recursive**) | ICLR 🏆 Outstanding | 2025 | ~417 | [💻](https://github.com/ShengranHu/ADAS) |
| [**GPTSwarm: Language Agents as Optimizable Graphs**](https://arxiv.org/abs/2402.16823) | **M. Zhuge**, Wang, Kirsch, Faccio et al. (KAUST / **Recursive**) | ICML | 2024 | ~300 | [💻](https://github.com/metauto-ai/GPTSwarm) |
| [**MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework**](https://arxiv.org/abs/2308.00352) | Hong, **M. Zhuge**, Chen, Zheng et al. | ICLR | 2024 | ~3015 | [💻](https://github.com/geekan/MetaGPT) |
| [**Agent-as-a-Judge: Evaluate Agents with Agents**](https://arxiv.org/abs/2410.10934) | **M. Zhuge**, Zhao, Ashley, Wang et al. (**Recursive**) | arXiv | 2024 | ~196 | [💻](https://github.com/metauto-ai/agent-as-a-judge) |
| [**Intelligent Go-Explore: Standing on the Shoulders of Giant Foundation Models**](https://arxiv.org/abs/2405.15143) | C. Lu, **S. Hu**, **J. Clune** (UBC) | ICLR | 2025 | ~80 | [💻](https://github.com/conglu1997/intelligent-go-explore) |
| [**Automated Capability Discovery via Foundation Model Self-Exploration**](https://arxiv.org/abs/2502.07577) | C. Lu*, **S. Hu***, **J. Clune** (UBC / **Recursive**) | arXiv | 2025 | ~30 | — |
| [**Mindstorms in Natural Language-Based Societies of Mind**](https://arxiv.org/abs/2305.17066) | **M. Zhuge**, Liu, Faccio, Ashley et al. | arXiv | 2023 | ~144 | — |
| [**AI with Recursive Self-Improvement**](https://openreview.net/forum?id=RSI2026) | **M. Zhuge**, Zeng, Zhu, Yang, Chandra, Schmidhuber (**Recursive**) | ICLR Workshop | 2026 | — | — |

### Meta-Learning & Self-Improvement

| Paper | Authors | Venue | Year | Citations | Code |
|-------|---------|-------|------|-----------|------|
| [**Thought Cloning: Learning to Think while Acting by Imitating Human Thinking**](https://arxiv.org/abs/2306.00323) | **S. Hu**, **J. Clune** (UBC) | NeurIPS Spotlight | 2023 | ~80 | [💻](https://github.com/ShengranHu/Thought-Cloning) |
| [**Learning to Continually Learn via Meta-learning Agentic Memory Designs (ALMA)**](https://arxiv.org/abs/2602.07755) | Y. Xiong, **S. Hu**, **J. Clune** (UBC / **Recursive**) | arXiv 🏆 Best Paper | 2026 | ~30 | — |
| [**Learning to Continually Learn (ANML)**](https://arxiv.org/abs/2002.09571) | Beaulieu, Frati, Miconi, Lehman, Stanley, **Clune** et al. | arXiv | 2020 | ~255 | [💻](https://github.com/uvm-neurobotics-lab/ANML) |
| [**Quality-Diversity through AI Feedback (QDAIF)**](https://arxiv.org/abs/2310.13032) | Bradley, Dai, Teufel, Zhang, Oostermeijer, Bellagente, **Clune** et al. | ICLR | 2024 | ~82 | — |
| [**OMNI-EPIC: Open-Endedness via Models of Human Notions of Interestingness**](https://arxiv.org/abs/2405.15568) | Faldor, Zhang, Cully, **Clune** | ICLR | 2025 | ~69 | [💻](https://github.com/MaxenceFaldor/Omni-EPIC) |
| [**Generative Teaching Networks**](https://arxiv.org/abs/1912.07768) | Such, Rawal, Lehman, Stanley, **Clune** | ICML | 2020 | ~249 | — |
| [**PromptBreeder: Self-Referential Self-Improvement via Prompt Evolution**](https://arxiv.org/abs/2309.16797) | Fernando, Banarse, Michalewski, Osindero, **Rocktäschel** et al. (DeepMind) | arXiv | 2023 | ~538 | — |
| [**Coconut: Training LLMs to Reason in a Continuous Latent Space**](https://arxiv.org/abs/2412.06769) | Hao, Sukhbaatar, Su, Li, Hu, Weston, **Y. Tian** (**Recursive** / Meta) | COLM | 2025 | ~570 | — |
| [**GaLore: Memory-Efficient LLM Training by Gradient Low-Rank Projection**](https://arxiv.org/abs/2403.03507) | Zhao, Zhang, Chen, Wang, Anandkumar, **Y. Tian** (Meta) | ICML Oral | 2024 | ~800 | — |
| [**StreamingLLM: Efficient Streaming Language Models with Attention Sinks**](https://arxiv.org/abs/2309.17453) | Xiao, **Y. Tian**, Chen, Han, Lewis (Meta) | ICLR | 2024 | ~1200 | — |
| [**ELF OpenGo: An Open Reimplementation of AlphaZero**](https://arxiv.org/abs/1902.04522) | **Y. Tian**, Ma, Gong, Sengupta et al. (Meta) | ICML Oral | 2019 | ~350 | — |

### Open-Ended Learning & Curriculum

| Paper | Authors | Venue | Year | Citations | Code |
|-------|---------|-------|------|-----------|------|
| [**Prioritized Level Replay**](https://arxiv.org/abs/2010.03934) | Jiang, Grefenstette, **Rocktäschel** | ICML | 2021 | ~266 | [💻](https://github.com/facebookresearch/level-replay) |
| [**Evolving Curricula with Regret-Based Environment Design**](https://arxiv.org/abs/2203.01302) | Jiang et al., **Rocktäschel** | ICML | 2022 | ~212 | [💻](https://github.com/facebookresearch/minimax) |
| [**Human-Timescale Adaptation in an Open-Ended Task Space**](https://arxiv.org/abs/2301.07608) | OEL Team, **Rocktäschel** et al. (DeepMind) | ICML | 2023 | ~82 | — |
| [**A Survey of Zero-Shot Generalisation in Deep Reinforcement Learning**](https://jair.org/index.php/jair/article/view/14174) | Kirk, Zhang, Grefenstette, **Rocktäschel** | JAIR | 2023 | ~420 | — |
| [**Voyager: An Open-Ended Embodied Agent with Large Language Models**](https://arxiv.org/abs/2305.16291) | G. Wang, Xie, Jiang, Mandlekar, Xiao, Zhu, Fan, Anandkumar (NVIDIA) | arXiv | 2023 | ~2506 | [💻](https://github.com/MineDojo/Voyager) |
| [**BALROG: Benchmarking Agentic LLM and VLM Reasoning on Games**](https://arxiv.org/abs/2411.13543) | Paglieri, Cupial, Parker-Holder, **Rocktäschel** | ICLR | 2025 | ~116 | [💻](https://github.com/balrog-ai/BALROG) |

### Prompt, Reward & Code Automation

| Paper | Authors | Venue | Year | Citations | Code |
|-------|---------|-------|------|-----------|------|
| [**Eureka: Human-Level Reward Design via Coding LLMs**](https://arxiv.org/abs/2310.12931) | Ma, Liang, Wang, Huang et al. (NVIDIA / CMU) | ICLR | 2024 | ~850 | [💻](https://github.com/eureka-research/Eureka) |
| [**OPRO: Large Language Models as Optimizers**](https://arxiv.org/abs/2309.03409) | Yang, Wang, Li, Fang et al. (Google DeepMind) | arXiv | 2023 | ~800 | [💻](https://github.com/google-deepmind/opro) |
| [**DSPy: Compiling Declarative Language Model Calls**](https://arxiv.org/abs/2310.03714) | Khattab, Singhvi, Maheshwari et al. (Stanford) | ICLR | 2024 | ~1200 | [💻](https://github.com/stanfordnlp/dspy) |
| [**Accelerating Multi-Objective NAS by Random-Weight Evaluation**](https://arxiv.org/abs/2110.05242) | **S. Hu**, Cheng, He, Lu, Wang, Zhang | Complex & Intelligent Systems | 2021 | ~80 | — |

### Surveys & Position Papers

| Paper | Authors | Venue | Year | Citations | Code |
|-------|---------|-------|------|-----------|------|
| [**Agentic AI for Scientific Discovery: A Survey**](https://arxiv.org/abs/2503.14517) | Gridach, Nanavati et al. | arXiv | 2025 | ~160 | — |
| [**From Automation to Autonomy: A Survey on LLMs in Scientific Discovery**](https://arxiv.org/abs/2505.13259) | Zheng, Deng et al. | ACL | 2025 | ~89 | — |
| [**A Survey of Zero-Shot Generalisation in Deep RL**](https://jair.org/index.php/jair/article/view/14174) | Kirk, Zhang, Grefenstette, Rocktäschel | JAIR | 2023 | ~420 | — |
| [**Automated Design of Agentic Systems: A Survey**](https://arxiv.org/abs/2408.08435) | Madžar, Mekterović | Preprints | 2026 | — | — |

---

## 🛠️ Open-Source Tools & Repos

> ⭐ = GitHub stars (approx) | 🔥 = actively maintained | 🆕 = < 6 months old

### Core Frameworks

| Repo | Description | Stars | Status |
|------|-------------|-------|--------|
| [**SakanaAI/AI-Scientist**](https://github.com/SakanaAI/AI-Scientist) | End-to-end automated ML research pipeline | ~10k | 🔥 |
| [**SakanaAI/AI-Scientist-v2**](https://github.com/SakanaAI/AI-Scientist-v2) | Agentic tree search version; workshop-accepted papers | ~4k | 🔥 🆕 |
| [**ShengranHu/ADAS**](https://github.com/ShengranHu/ADAS) | Automated Design of Agentic Systems (Meta Agent Search) | ~800 | 🔥 |
| [**metauto-ai/GPTSwarm**](https://github.com/metauto-ai/GPTSwarm) | Language agents as optimizable graphs | ~1 | 🔥 |
| [**geekan/MetaGPT**](https://github.com/geekan/MetaGPT) | Multi-agent collaborative framework | ~48k | 🔥 |
| [**metauto-ai/agent-as-a-judge**](https://github.com/metauto-ai/agent-as-a-judge) | Agent-based evaluation framework | ~400 | 🔥 |
| [**SamuelSchmidgall/AgentLaboratory**](https://github.com/SamuelSchmidgall/AgentLaboratory) | LLM agents as research assistants | ~2k | 🔥 |
| [**google-deepmind/funsearch**](https://github.com/google-deepmind/funsearch) | LLM + evolutionary search for mathematical discovery | ~3k | 🔥 |
| [**stanfordnlp/dspy**](https://github.com/stanfordnlp/dspy) | Declarative LM program optimization | ~22k | 🔥 |

### Open-Ended Learning

| Repo | Description | Stars | Status |
|------|-------------|-------|--------|
| [**facebookresearch/level-replay**](https://github.com/facebookresearch/level-replay) | Prioritized Level Replay for RL generalization | ~300 | ✅ |
| [**facebookresearch/minimax**](https://github.com/facebookresearch/minimax) | Unsupervised environment design (ACCEL, PLR) | ~250 | ✅ |
| [**MineDojo/Voyager**](https://github.com/MineDojo/Voyager) | Open-ended LLM agent in Minecraft | ~5k | ✅ |
| [**MaxenceFaldor/Omni-EPIC**](https://github.com/MaxenceFaldor/Omni-EPIC) | Open-endedness via human interestingness models | ~200 | 🔥 |
| [**jennyzzt/dgm**](https://github.com/jennyzzt/dgm) | Darwin Gödel Machine: self-improving agents | ~600 | 🔥 🆕 |

### Reward & Prompt Automation

| Repo | Description | Stars | Status |
|------|-------------|-------|--------|
| [**eureka-research/Eureka**](https://github.com/eureka-research/Eureka) | Human-level reward design with LLMs | ~2k | ✅ |
| [**google-deepmind/opro**](https://github.com/google-deepmind/opro) | LLMs as optimizers for prompts | ~1 | ✅ |

### Benchmarks & Evaluation

| Repo | Description | Stars | Status |
|------|-------------|-------|--------|
| [**openai/mle-bench**](https://github.com/openai/mle-bench) | ML engineering benchmark (75 Kaggle competitions) | ~2 | 🔥 |
| [**princeton-nlp/SWE-bench**](https://github.com/princeton-nlp/SWE-bench) | Software engineering agent benchmark | ~5k | 🔥 |
| [**facebookresearch/MLGym**](https://github.com/facebookresearch/MLGym) | Framework for AI research agents | ~400 | 🔥 🆕 |
| [**balrog-ai/BALROG**](https://github.com/balrog-ai/BALROG) | LLM/VLM reasoning on games | ~300 | 🔥 |
| [**conglu1997/intelligent-go-explore**](https://github.com/conglu1997/intelligent-go-explore) | Foundation model guided Go-Explore | ~200 | ✅ |

### Infrastructure & Utilities

| Repo | Description | Stars | Status |
|------|-------------|-------|--------|
| [**uvm-neurobotics-lab/ANML**](https://github.com/uvm-neurobotics-lab/ANML) | A neuromodulatory meta-learning framework | ~150 | ✅ |
| [**ShengranHu/Thought-Cloning**](https://github.com/ShengranHu/Thought-Cloning) | Imitation learning with language-based thinking | ~150 | ✅ |
| [**wjlgatech/ToolUniverse**](https://github.com/wjlgatech/ToolUniverse) | Ecosystem (1000+ tools) for building AI scientist systems; MCP-native, async, composable | 🆕 | 🔥 |

### Existing "Awesome" Lists & What's Missing

| Repo | Description | Stars | Status |
|------|-------------|-------|--------|
| [**yenanjing/awesome-ai-for-science**](https://github.com/yenanjing/awesome-ai-for-science) |  | ~4 |  |

---

## 🏅 Certified Tooling

Tools here earn an **evidence-backed** tier, not an install count — the trust layer [skills.sh](https://www.skills.sh/) lacks. **0 🥇 Certified · 19 🥈 Verified · 21 🥉 Listed.**

🥈 Verified = relevant + maintained (machine-checked). 🥇 adds *works* + *safe* via `anyagent analyze`/`brace`; no-evidence ⇒ no badge. → **[Full certified list](docs/CERTIFIED.md)** · [raw data](knowledge/certifications.json)

---

## 🧰 Certified Toolsets

Every top repo cited here is minted into a reusable **agentic skill** + a knowledge graph (`scripts/repo_factory.py`). `/rsi` loads the **[registry](skills/registry.json)** as backbone; each skill's body loads on-demand (**progressive disclosure**) when its trigger matches your task.

**19 toolsets** — AI-Scientist, AI-Scientist-v2, AgentLaboratory, HyperAgents, MLGym, PraisonAI, agent-as-a-judge, bitrouter, codemesh, dgm, dspy, file-system-like-github…

→ **[Browse the toolset registry](skills/README.md)** · per-repo graphs in `knowledge/repos/`

---

## 👥 People & Labs to Follow

### 🎯 Recursive Lab — 8 Co-Founders & Key Members

> **Recursive** (recursive.com) — "Recursive self-improving superintelligence to automate knowledge discovery."
> Founded May 2026 · Raised **$650M at $4.65B valuation** led by GV (Google Ventures) & Greycroft, with AMD Ventures & NVIDIA
> Offices in San Francisco & London · 25+ team members from OpenAI, DeepMind, Meta AI, Google Brain, Salesforce AI, Uber AI

#### The 8 Co-Founders

| Person | Previous Roles | Research Focus | Key Papers | Links |
|--------|---------------|----------------|------------|-------|
| **Jeff Clune** | OpenAI, Uber AI | AI-GAs, open-ended learning, quality diversity, meta-learning | AI-GAs (2019), ADAS (2025), DGM (2026), AI Scientist (2026) | [🌐](https://jeffclune.com) [𝕏](https://x.com/jeffclune) [Scholar](https://scholar.google.com/citations?user=5eeQ9AkAAAAJ) [LinkedIn](https://www.linkedin.com/in/jeff-clune/) |
| **Tim Rocktäschel** | Meta AI (FAIR), UCL | Open-endedness, RL, curriculum learning, ASI | PLR (2021), ACCEL (2022), PromptBreeder (2023), Open-Endedness Essential (2024) | [🌐](https://rockt.ai) [𝕏](https://x.com/_rockt) [Scholar](https://scholar.google.com/citations?user=gLskPY0AAAAJ) [LinkedIn](https://www.linkedin.com/in/tim-rocktaeschel/) |
| **Richard Socher** | Salesforce AI (SVP), Stanford | NLP, LLMs, deep learning, you.com founder | GloVe (2014), Dynamic Memory Networks (2016), CoVe (2017) | [🌐](https://www.socher.org) [𝕏](https://x.com/RichardSocher) [Scholar](https://scholar.google.com/citations?user=FaOcyfMAAAAJ) [LinkedIn](https://www.linkedin.com/in/richard-socher/) |
| **Caiming Xiong** | Salesforce AI (SVP Research), Cresta | LLMs, code generation, multi-agent systems | CoVe / Learned in Translation (2017), OpenAgents (2023) | [𝕏](https://x.com/CaimingXiong) [Scholar](https://scholar.google.com/citations?user=vACNGQsAAAAJ) [LinkedIn](https://www.linkedin.com/in/caiming-xiong/) |
| **Yuandong Tian** | Meta AI (Research Scientist Director), Google | LLM reasoning, RL, planning, self-supervised learning, NAS | Coconut/COLM (2025), GaLore/ICML Oral (2024), StreamingLLM/ICLR (2024), ELF OpenGo/ICML Oral (2019), DirectPred/ICML Outstanding (2021) | [🌐](https://yuandong-tian.com) [𝕏](https://x.com/yuandong_tian) [Scholar](https://scholar.google.com/citations?user=GR3ly80AAAAJ) [LinkedIn](https://www.linkedin.com/in/yuandong-tian/) |
| **Tim Shi** | OpenAI (early), Cresta (Co-Founder) | Applied AI, LLM products | — | [𝕏](https://x.com/timshi) [LinkedIn](https://www.linkedin.com/in/timshi/) |
| **Mingchen Zhuge** | KAUST | Multi-agent systems, recursive self-improvement, LLM optimization | GPTSwarm/ICML (2024), MetaGPT/ICLR (2024), Agent-as-a-Judge (2024), Mindstorms (2023) | [𝕏](https://x.com/MingchenZhuge) [Scholar](https://scholar.google.com/citations?user=MingchenZhuge) [LinkedIn](https://www.linkedin.com/in/mingchenzhuge/) |
| **Yingbo Zhou** | Salesforce AI, Uber AI | LLMs, multi-agent, AI research automation | — | [LinkedIn](https://www.linkedin.com/in/yingbozhou/) |

#### Founding Mission (from [stealth launch blog post](https://www.linkedin.com/pulse/we-emerging-from-stealth-bold-bet-self-improving-ai-recursive-si-9jwwc/), May 2026)

> *"We are former research team leaders from OpenAI, Google DeepMind, Meta AI, Salesforce AI, and Uber AI. We raised $650M at $4.65 billion valuation to create AI that conducts experiments on how to safely improve itself—in an open-ended process of automated scientific discovery. This will likely be the fastest path to superintelligence."*

#### Other Key Team Members

| Person | Role | Research Focus | Links |
|--------|------|----------------|-------|
| **Shengran Hu** | Founding Member (PhD student, UBC under Jeff Clune) | Automated agentic systems, self-improvement, NAS | [🌐](https://shengranhu.com) [𝕏](https://x.com/ShengranHu) [Scholar](https://scholar.google.com/citations?user=ShengranHu) [GitHub](https://github.com/ShengranHu) [LinkedIn](https://www.linkedin.com/in/shengranhu/) |
| **Josh Tobin** | Automating Scientific Discovery | Sim-to-real robotics, automated discovery | [𝕏](https://x.com/josh_tobin_) [Scholar](https://scholar.google.com/citations?user=josh_tobin) [LinkedIn](https://www.linkedin.com/in/josh-tobin-4b3b10a/) |
| **Peter Norvig** | Researcher / Education Fellow Stanford | AI foundations, rationality, education | [🌐](https://norvig.com) [Scholar](https://scholar.google.com/citations?user=2XoHRgEAAAAJ) [LinkedIn](https://www.linkedin.com/in/pnorvig/) |
| **Jianguo Zhang** | Founding Member | LLM agents, multi-agent | [LinkedIn](https://www.linkedin.com/in/jiguozhang/) |


### 🔬 Affiliated Researchers

| Person | Affiliation | Focus | Links |
|--------|-------------|-------|-------|
| **Cong Lu** | UBC / Sakana AI | AI Scientist, automated discovery | [𝕏](https://x.com/CongLu_) [Scholar](https://scholar.google.com/citations?user=conglu) [GitHub](https://github.com/conglu1997) |
| **Robert Tjarko Lange** | Sakana AI | AI Scientist, evolutionary methods | [𝕏](https://x.com/RobertTLange) [Scholar](https://scholar.google.com/citations?user=RobertTLange) [GitHub](https://github.com/RobertTLange) |
| **Chris Lu** | Oxford / Sakana AI | AI Scientist, RL | [𝕏](https://x.com/ChrisLu_RL) [GitHub](https://github.com/chrislu) |
| **Jakob Foerster** | Oxford | Multi-agent RL, emergent communication | [🌐](https://www.jakobfoerster.com) [𝕏](https://x.com/j_foerst) |
| **David Ha** | Sakana AI | Generative models, AI for science | [🌐](https://otoro.net) [𝕏](https://x.com/hardmaru) |
| **Jack Parker-Holder** | Google DeepMind | Open-endedness, AutoRL | [𝕏](https://x.com/jparkerholder) |
| **Jenny Zhang** | UBC / Sakana AI | Darwin Gödel Machine, evolution | [𝕏](https://x.com/jennyzzt_) [GitHub](https://github.com/jennyzzt) |
| **Minqi Jiang** | UCL / DeepMind | Curriculum learning, UED | [𝕏](https://x.com/minqi_jiang) [Scholar](https://scholar.google.com/citations?user=minqi_jiang) |

### 🏢 Key Labs

| Lab | Focus | Links |
|-----|-------|-------|
| **Recursive (Recursive SI)** | Recursive self-improvement, automated knowledge discovery | [🌐](https://recursive.com) [LinkedIn](https://linkedin.com/company/recursive-si) [𝕏](https://x.com/RecursiveSI) |
| **Sakana AI** | AI Scientist, evolutionary AI, foundation models | [🌐](https://sakana.ai) [𝕏](https://x.com/SakanaAILabs) [GitHub](https://github.com/SakanaAI) |
| **Google DeepMind (Open-Endedness)** | Open-endedness, AlphaEvolve, FunSearch, AI Co-Scientist | [🌐](https://deepmind.google) [𝕏](https://x.com/GoogleDeepMind) |
| **UCL DARK Lab** (Rocktäschel) | Open-ended RL, curriculum learning | [🌐](https://rockt.ai) [𝕏](https://x.com/_rockt) |
| **UBC (Clune Lab)** | AI-GAs, quality diversity, self-improvement | [🌐](https://jeffclune.com) [𝕏](https://x.com/jeffclune) |
| **Stanford AI Lab / NLP Group** | DSPy, CodeAct, autonomous agents | [🌐](https://ai.stanford.edu) [𝕏](https://x.com/stanfordai) |
| **Princeton NLP** | SWE-bench, autonomous coding | [🌐](https://nlp.cs.princeton.edu) [GitHub](https://github.com/princeton-nlp) |
| **KAUST (MetaAutoAI)** | Multi-agent systems, GPTSwarm | [GitHub](https://github.com/metauto-ai) |
| **OpenAI** | MLE-Bench, Codex, autonomous agents | [🌐](https://openai.com) [𝕏](https://x.com/OpenAI) [GitHub](https://github.com/openai) |

---

## 🎙️ Talks, Interviews & Podcasts

| Title | Speaker(s) | Event | Year | Link |
|-------|-----------|-------|------|------|
| **Open-Ended and AI-Generating Algorithms in the Era of Foundation Models** | Jeff Clune (**Recursive**) | U Toronto / Vector Institute | 2025 | [▶️](https://jeffclune.com/videos.html) |
| **Open-Ended and AI-Generating Algorithms in the Era of Foundation Models** | Jeff Clune (**Recursive**) | University of Oxford | 2024 | [▶️](https://jeffclune.com/videos.html) |
| **ICLR 2025 Keynote: Open-Endedness & ASI** | Tim Rocktäschel (**Recursive** / UCL) | ICLR | 2025 | [▶️](https://iclr.cc/virtual/2025/index.html) |
| **Improving Deep RL via QD, Open-Ended and AI-Generating Algorithms** | Jeff Clune (**Recursive**) | MIT / CORL Keynote | 2023/2021 | [▶️](https://jeffclune.com/videos.html) |
| **How Meta-Learning Could Help Us Accomplish Our Grandest AI Ambitions** | Jeff Clune (**Recursive**) | NeurIPS Meta-Learning Workshop | 2019 | [▶️](https://jeffclune.com/videos.html) |
| **The AI Scientist: Fully Automated Scientific Discovery** | Chris Lu, David Ha (Sakana AI) | Various | 2024 | [▶️](https://sakana.ai/ai-scientist) |
| **Why I Work on Self-Improving AI Despite the Risks** | Jeff Clune (**Recursive**) | Blog / Essay | 2024 | [📖](https://jeffclune.com) |
| **Lex Fridman Podcast: Automated AI Research** | Multiple guests | Lex Fridman | 2024–25 | [▶️](https://lexfridman.com/podcast) |
| **NVIDIA Research: Eureka — Human-Level Reward Design** | Yecheng Jason Ma | NVIDIA Tech Blog | 2024 | [▶️](https://eureka-research.github.io) |
| **Go-Explore: A New Type of Algorithm for Hard-Exploration Problems** | Jeff Clune (**Recursive**) | ReWork 2019 | 2019 | [▶️](https://jeffclune.com/videos.html) |
| **Learning Beyond Gradients: Heuristic Learning & Continual Learning** | Jiayi Weng (**Recursive**) | Blog / Essay | 2025 | [💻](https://trinkle23897.github.io/learning-beyond-gradients/) |

---

## 📈 Benchmarks & Leaderboards

### Benchmarks & Evaluation

| Benchmark | Focus | Venue | Year | Citations |
|-----------|-------|-------|------|-----------|
| [**MLE-Bench**](https://arxiv.org/abs/2410.07095) | ML engineering (75 Kaggle tasks) | ICLR | 2025 | ~349 |
| [**SWE-bench**](https://arxiv.org/abs/2310.06770) | Software engineering (GitHub issues) | ICLR | 2024 | ~1000 |
| [**MLGym**](https://arxiv.org/abs/2502.14499) | AI research agent framework | arXiv | 2025 | ~88 |
| [**BALROG**](https://arxiv.org/abs/2411.13543) | Agentic LLM reasoning on games | ICLR | 2025 | ~116 |
| [**EXP-Bench**](https://arxiv.org/abs/2505.24785) | AI conducting AI research experiments | arXiv | 2025 | ~23 |
| [**Agent-as-a-Judge**](https://arxiv.org/abs/2410.10934) | Evaluating agents with agents | arXiv | 2024 | ~196 |

### Benchmarks & Leaderboards

| Benchmark | Focus | Venue | Year | Citations |
|-----------|-------|-------|------|-----------|
| [**SWE-bench Verified**](https://swebench.com) | Fix real GitHub issues |  |  | — |
| [**AI Scientist Review Score**](https://github.com/SakanaAI/AI-Scientist) | Auto-generated paper quality |  |  | — |
| [**Aider Leaderboard**](https://aider.chat/docs/leaderboards/) | Code editing (SWE-bench style) |  |  | — |

---

## 🛰️ Frontier Radar

_The latest surfaced from the people we follow via open arXiv/GitHub APIs (`scripts/track.py`, refreshed weekly). Surname-matched — verify the author._

| Researcher | Most recent work | Date |
|-----------|------------------|------|
| Caiming Xiong | [Pancasila-Dilemmas: Evaluating Large Language Models on Indonesian Human Value Dilemmas Grounded in Pancasila](http://arxiv.org/abs/2607.18066v1) | 2026-07-20 |
| Chris Lu | [Automated Discovery Has No Universally Superior Harness](http://arxiv.org/abs/2607.18235v1) | 2026-07-20 |
| Cong Lu | [Automated Discovery Has No Universally Superior Harness](http://arxiv.org/abs/2607.18235v1) | 2026-07-20 |
| David Ha | [Simple Domain Generalization for Strong Pixel-Level Image Tampering Detection in Modern VLMs](http://arxiv.org/abs/2607.18230v1) | 2026-07-20 |
| Jakob Foerster | [How the Quantum Sorites Phenomenon Strengthens the Bell Argument and How a Random-Matrix Collapse Dynamics Answers It](http://arxiv.org/abs/2607.17894v1) | 2026-07-20 |
| Jenny Zhang | [Color superconductors and holon metals from doping a Fractional Chern insulator](http://arxiv.org/abs/2607.18238v1) | 2026-07-20 |
| Jianguo Zhang | [Color superconductors and holon metals from doping a Fractional Chern insulator](http://arxiv.org/abs/2607.18238v1) | 2026-07-20 |
| Minqi Jiang | [HOMIE: Human-object Centric Video Personalization via Multimodal Intelligent Enchancement](http://arxiv.org/abs/2607.18217v1) | 2026-07-20 |

---

## 📅 Timeline: Key Milestones

```
2003  Gödel Machine (Schmidhuber) — theoretical foundation of self-improving AI
2019  AI-GAs (Clune) — vision for automating AI creation; POET open-ended evolution
2020  ANML (Clune et al.) — meta-learned continual learning
2021  Prioritized Level Replay (Rocktäschel) — automatic curriculum for RL
2022  Evolving Curricula / ACCEL (Rocktäschel)
2023  PromptBreeder (Rocktäschel, DeepMind) — self-referential prompt evolution
       Thought Cloning (S. Hu & Clune) — NeurIPS Spotlight
       Voyager (NVIDIA) — open-ended LLM agent in Minecraft
       MetaGPT (M. Zhuge et al.) — meta-programming for multi-agent systems
       GPTSwarm (M. Zhuge et al.) — agents as optimizable graphs
2024  The AI Scientist v1 (Lu, S. Hu, Clune, Ha et al.) — first fully automated research
       ADAS — Automated Design of Agentic Systems (S. Hu, Clune)
       Eureka — human-level reward design via LLMs
       BALROG (Rocktäschel et al.) — agentic LLM benchmark
       AI Co-Scientist (Google DeepMind) — hypothesis generation pipeline
       FunSearch (Google DeepMind) — mathematical discoveries via LLM + evolution
       Agent-as-a-Judge (M. Zhuge, Recursive)
2025  The AI Scientist v2 (Yamada, Lange, S. Hu et al.) — workshop papers accepted
       Darwin Gödel Machine (Zhang, S. Hu, Clune) — ICLR 2026
       AlphaEvolve (Google DeepMind) — coding agent for algorithm discovery
       MLGym, MLE-Bench, BALROG — benchmark ecosystem matures
       ALMA — meta-learned agentic memory designs (S. Hu, Clune) — Best Paper
2026  AI Scientist Nature paper published — Vol. 651, pp. 914–919
       Recursive emerging from stealth: $650M at $4.65B valuation (GV, Greycroft, AMD, NVIDIA)
       8 co-founders announced: Clune, Rocktäschel, Socher, Caiming Xiong, Yuandong Tian, Tim Shi, M. Zhuge, Y. Zhou
       AI with Recursive Self-Improvement workshop @ ICLR (M. Zhuge, Recursive)
       Recursive co-founded — Jeff Clune, Tim Rocktäschel, Richard Socher, Caiming Xiong
```

---

## 🗺️ Learning Roadmaps

### Beginner Path (0–3 months)

```
WEEK 1-2: Foundations
├── Read: "AI-GAs" (Clune 2019) — the big vision [30 min]
├── Watch: Jeff Clune's Oxford talk (2024) [60 min]
├── Read: "Voyager" paper summary [20 min]
└── Try: Run MetaGPT's hello-world example [2 hours]

WEEK 3-4: Core Papers
├── Read: "ADAS" paper (Hu, Lu, Clune 2025) [1 hour]
├── Read: "The AI Scientist" paper (2024) [2 hours]
├── Watch: AI Scientist demo videos on Sakana website [30 min]
└── Try: Run AI Scientist on NanoGPT template [$10-30 API cost]

MONTH 2: Go Deeper
├── Read: "MetaGPT" (Zhuge et al. 2024) — multi-agent design [1 hour]
├── Read: "Agent-as-a-Judge" (Zhuge et al. 2024) [30 min]
├── Try: GPTSwarm demo notebook [1-2 hours]
├── Read: "PromptBreeder" (Rocktäschel et al.) [1 hour]
└── Try: DSPy for automated prompt optimization [2 hours]

MONTH 3: Benchmark Yourself
├── Read: "MLE-Bench" paper [1 hour]
├── Try: Run an agent on SWE-bench Lite [4-8 hours]
├── Explore: BALROG benchmark leaderboard
└── Join: Discord communities (MetaGPT, DSPy)
```

### Advanced Researcher Path

```
PHASE 1: Master the Landscape (1-2 months)
├── Read all papers in this repo (foundational → recent)
├── Reproduce: ADAS Meta Agent Search on a new domain
├── Reproduce: AI Scientist on a custom template
├── Deep dive: Open-endedness theory (Hughes et al. 2024)
└── Study: Gödel Machine → AI-GAs → Darwin Gödel Machine lineage

PHASE 2: Identify Research Gaps (2-3 months)
├── Where does AI Scientist fail? (template dependency, evaluation)
├── ADAS limitations? (search efficiency, safety, generalization)
├── Open problems: multi-modal AI scientist, real-world lab automation
├── Safety: how do self-improving systems stay aligned?
└── Read: "AI with Recursive Self-Improvement" (Zhuge, Recursive, ICLR 2026)

PHASE 3: Contribute (ongoing)
├── Submit PRs to this repo with new papers / tools
├── Release code for your experiments
├── Benchmark on MLE-Bench or SWE-bench
├── Present at ICLR RSI Workshop / NeurIPS AutoML Workshop
└── Follow: @jeffclune @_rockt @ShengranHu on 𝕏

KEY OPEN PROBLEMS (as of June 2026):
• Automated theory generation (beyond ML experiments)
• Verified self-improvement with formal safety guarantees
• Cross-domain knowledge transfer in automated discovery
• Human-AI collaboration protocols in research pipelines
• Evaluation: what makes a good automated research system?
```

---

## 🏆 Competitive Landscape Analysis

### Existing "Awesome" Lists & What's Missing

| Repo | Stars | Last Updated | Gap |
|------|-------|--------------|-----|
| [yenanjing/awesome-ai-for-science](https://github.com/yenanjing/awesome-ai-for-science) | 4 | June 2026 | No Recursive Lab focus; no people/talks |
| General "awesome-llm-agents" lists | 1k–5k | Varies | Broad scope; miss self-improvement thread |

### What Makes This Repo Different

1. **Only list focused on the Recursive Lab ecosystem** — founders, papers, and intellectual lineage
2. **Dual beginner + advanced roadmaps** — actionable learning paths
3. **Citation counts + reproducibility status** on every paper
4. **Cross-linked ecosystem** — paper ↔ code ↔ people ↔ lab
5. **Timeline** — shows the evolution from Gödel Machine to Nature paper
6. **Open-endedness thread** — captures Rocktäschel's full research arc
7. **Community contribution framework** — designed for viral growth

---

## 🤝 How to Contribute

This list thrives on community contributions. Here's how to add value:

### Quick Contributions
- ⭐ **Star this repo** to boost visibility
- 🐦 **Share on 𝕏** tagging [@wjlgatech](https://x.com/wjlgatech), [@jeffclune](https://x.com/jeffclune), [@_rockt](https://x.com/_rockt), [@ShengranHu](https://x.com/ShengranHu)
- 💼 **Share on LinkedIn** tagging [Recursive](https://linkedin.com/company/recursive-si)

### Submit a PR
1. Fork this repo
2. Add your paper/tool/resource following the existing table format
3. Include: title, authors (bold **Recursive** members), venue, year, citations, code link
4. Submit PR with title: `Add: [Paper/Tool/Person] - [Brief description]`

### What We're Looking For
- 📄 New papers on automated AI research (cite count > 20, or from Recursive/Sakana/DeepMind)
- 🛠️ Open-source tools with > 100 GitHub stars
- 🎙️ Talks from Recursive Lab members or leading researchers in the field
- 🏆 New benchmarks for measuring automated research quality
- 🔗 Blog posts, tutorials, course materials

### Quality Standards
- Papers must be peer-reviewed OR from a credible lab (arXiv ok if > 50 citations or very recent)
- Tools must have a working demo or README
- No promotional content without genuine research value

---

## 📜 Citation

If this resource helps your research, please cite:

```bibtex
@misc{wu2026awesomeautoairesearch,
  author = {Wu, Paul Jialiang},
  title = {Awesome Automated AI Research},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/wjlgatech/rsi-os}}
}
```

---

<div align="center">

**⭐ If this helped you, please star the repo and share with your network!**

Maintained with ❤️ by [Paul Jialiang Wu (@wjlgatech)](https://github.com/wjlgatech) and the community.

*Updated: June 2026 | Next review: September 2026*

[![Twitter Follow](https://img.shields.io/twitter/follow/wjlgatech?style=social)](https://x.com/wjlgatech)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/jialiang-wu-67aa7179/)

</div>

---

<sub>README generated from <code>data/*.yml</code> + <code>data/prose/*.md</code> by <code>scripts/build_readme.py</code> — do not edit by hand; run <code>make build</code>.</sub>
