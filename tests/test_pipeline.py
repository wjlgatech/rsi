#!/usr/bin/env python3
"""Test suite for the RSI auto-sync + certification pipeline.

Stdlib-only (unittest) to preserve the repo's zero-dependency ethos. This is the
verification layer that makes the CODE a closed loop, not just the data: every pure
function that a weekly run relies on is pinned here, so `make check` can catch a
regression before a PR ever opens. Run: python3 -m unittest discover -s tests
"""
import datetime as dt
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "ingest"))

import github_sync as gh      # noqa: E402
import skills_sync as sk      # noqa: E402
import mcp_sync as mcp        # noqa: E402
import workflows_sync as wf   # noqa: E402
import groundbreakers as gb   # noqa: E402
import certify as cert        # noqa: E402
import certify_gold as gold   # noqa: E402
import check_ingest as chk    # noqa: E402


class TestGithubSync(unittest.TestCase):
    README = (
        "[![Stars](https://img.shields.io/github/stars/wjlgatech/awesome-auto-ai-research)]"
        "(https://github.com/wjlgatech/awesome-auto-ai-research/stargazers)\n"
        "| [**stanfordnlp/dspy**](https://github.com/stanfordnlp/dspy) | Declarative LM | ~22k | 🔥 |\n"
        "| [**jennyzzt/dgm**](https://github.com/jennyzzt/dgm) | Darwin Gödel Machine | ~600 | 🔥 |\n"
        "| Gödel Machines paper | Schmidhuber | arXiv | 2003 | ~77 | [dspy](https://github.com/stanfordnlp/dspy) |\n"
    )

    def test_existing_repos_excludes_self_and_badges(self):
        slugs = gh.existing_repos(self.README)
        self.assertIn("stanfordnlp/dspy", slugs)
        self.assertIn("jennyzzt/dgm", slugs)
        self.assertNotIn("wjlgatech/awesome-auto-ai-research", slugs)  # self-repo dropped

    def test_printed_star_k_suffix(self):
        self.assertEqual(gh.printed_star(self.README, "stanfordnlp/dspy"), 22000)

    def test_printed_star_ignores_year_from_paper_row(self):
        # dgm's own row prints ~600; the fn must not grab a citation/year from elsewhere
        self.assertEqual(gh.printed_star(self.README, "jennyzzt/dgm"), 600)

    def test_printed_star_prefers_bold_own_row_over_code_link(self):
        # dspy also appears as a paper's code link (row with year 2003, citations 77);
        # the star must come from its bold tools row (~22k), never the year 2003.
        self.assertEqual(gh.printed_star(self.README, "stanfordnlp/dspy"), 22000)

    def test_relevance_gate(self):
        self.assertTrue(gh.is_rsi_relevant("x/self-improving-agent", "recursive self improvement"))
        self.assertFalse(gh.is_rsi_relevant("microsoft/qlib", "AI-oriented quant investment platform"))


class TestGroundbreakers(unittest.TestCase):
    def test_rsi_relevant(self):
        on = {"title": "A Self-Evolving Agentic OS", "evidence": {"summary": ""}}
        off = {"title": "Fast image diffusion sampler", "evidence": {"summary": ""}}
        self.assertTrue(gb._rsi_relevant(on))
        self.assertFalse(gb._rsi_relevant(off))

    def test_pick_slate_seminal_is_on_topic(self):
        cands = [
            {"kind": "paper", "action": "add", "score": 200, "title": "Text-to-image reward",
             "evidence": {"authors": [], "summary": "diffusion"}},
            {"kind": "paper", "action": "add", "score": 150, "title": "Recursive self-improvement in agents",
             "evidence": {"authors": [], "summary": "self-improving"}},
        ]
        slate = gb.pick_slate(cands)
        self.assertIsNotNone(slate["seminal"])
        self.assertIn("Recursive", slate["seminal"]["title"])  # the fresher off-topic one lost

    def test_author_bonus_is_tiebreaker_not_override(self):
        # a co-founder's off-topic paper must NOT win the on-topic slot
        cands = [
            {"kind": "paper", "action": "add", "score": 100, "title": "Open-ended learning curriculum",
             "evidence": {"authors": ["nobody"], "summary": "open-ended"}},
            {"kind": "paper", "action": "add", "score": 90, "title": "Time series forecasting",
             "evidence": {"authors": ["Yuandong Tian"], "summary": "forecasting"}},
        ]
        slate = gb.pick_slate(cands)
        self.assertIn("Open-ended", slate["seminal"]["title"])


class TestSkillsSync(unittest.TestCase):
    def test_reuses_github_relevance_gate(self):
        # unit 1's discovery must reject a generic high-star repo and keep a real RSI skill
        self.assertTrue(sk.gh.is_rsi_relevant("x/self-learning-skills", "self-improving skill for agents"))
        self.assertFalse(sk.gh.is_rsi_relevant("microsoft/qlib", "quant investment platform"))

    def test_has_query_set(self):
        self.assertTrue(len(sk.SKILL_QUERIES) >= 3)


class TestMcpAndWorkflows(unittest.TestCase):
    def test_workflow_hint_gate(self):
        self.assertTrue(wf._is_workflow("x/agent-pipeline", "self-improving orchestration workflow"))
        self.assertFalse(wf._is_workflow("x/thing", "a static website"))

    def test_adapters_have_queries(self):
        self.assertTrue(len(mcp.MCP_QUERIES) >= 3)
        self.assertTrue(len(wf.WORKFLOW_QUERIES) >= 3)


class TestGoldSafetyScan(unittest.TestCase):
    def _scan(self, files: dict):
        import tempfile
        d = tempfile.mkdtemp(prefix="rsi-test-")
        for name, body in files.items():
            with open(os.path.join(d, name), "w") as f:
                f.write(body)
        try:
            return gold.score_safe(d)
        finally:
            import shutil
            shutil.rmtree(d, ignore_errors=True)

    def test_clean_repo_scores_100(self):
        score, findings = self._scan({"main.py": "def f():\n    return 1\n"})
        self.assertEqual(score, 100)
        self.assertEqual(findings, [])

    def test_committed_secret_is_near_disqualifying(self):
        score, findings = self._scan({"cfg.py": "KEY = 'sk-abcdefghijklmnopqrstuvwxyz012345'"})
        self.assertLessEqual(score, 40)
        self.assertTrue(any("secret" in f for f in findings))

    def test_remote_exec_pipeline_flagged(self):
        score, findings = self._scan({"install.sh": "curl https://x.io/i.sh | sudo bash\n"})
        self.assertLess(score, 100)
        self.assertTrue(any("risky exec" in f for f in findings))


class TestCertify(unittest.TestCase):
    TODAY = dt.date(2026, 7, 14)

    def test_curated_tool_gets_relevance_floor(self):
        # a curated repo with a terse summary (dspy) must not be disqualified on relevance
        node = {"id": "r", "name": "stanfordnlp/dspy", "summary": "Declarative LM programs",
                "stars": 22000, "pushed": "2026-07-01", "curated": True, "kind": "repo"}
        c = cert.certify_tool(node, self.TODAY)
        self.assertGreaterEqual(c["scores"]["relevant"], 60)
        self.assertEqual(c["tier"], "🥈 Verified")

    def test_skill_certifies_from_signals(self):
        # a real discovered skill (2+ lexicon hits in name+summary, fresh push) → Verified
        node = {"id": "s", "name": "x/self-learning-skills", "summary": "self-improving skill for AI agents",
                "stars": 800, "pushed": "2026-07-05", "curated": False, "kind": "skill"}
        c = cert.certify_tool(node, self.TODAY)
        self.assertEqual(c["kind"], "skill")
        self.assertEqual(c["scores"]["relevant"], 80)
        self.assertEqual(c["tier"], "🥈 Verified")  # relevant+maintained, works/safe not_measured

    def test_weak_relevance_skill_stays_listed(self):
        # one lexicon hit is weak evidence — honestly 🥉, not Verified (no relevance floor for
        # non-curated tools; only human-vetted list entries get the floor)
        node = {"id": "s2", "name": "x/thing", "summary": "an agent helper",
                "stars": 800, "pushed": "2026-07-05", "curated": False, "kind": "skill"}
        self.assertEqual(cert.certify_tool(node, self.TODAY)["tier"], "🥉 Listed")

    def test_maintained_bands(self):
        self.assertEqual(cert._maintained("2026-07-01", self.TODAY), 100)   # fresh
        self.assertEqual(cert._maintained("2025-10-01", self.TODAY), 60)    # <1yr
        self.assertEqual(cert._maintained("2023-01-01", self.TODAY), 20)    # stale
        self.assertEqual(cert._maintained(None, self.TODAY), cert.NOT_MEASURED)

    def test_tier_never_certified_without_works_and_safe(self):
        scores = {"relevant": 100, "maintained": 100, "adopted": 100,
                  "works": cert.NOT_MEASURED, "safe": cert.NOT_MEASURED}
        self.assertEqual(cert.tier(scores), "🥈 Verified")  # not 🥇 — no-evidence ⇒ No

    def test_tier_certified_only_when_all_blocking_pass(self):
        scores = {"relevant": 100, "maintained": 100, "adopted": 100, "works": 80, "safe": 90}
        self.assertEqual(cert.tier(scores), "🥇 RSI-Certified")

    def test_tier_listed_when_relevance_fails(self):
        scores = {"relevant": 0, "maintained": 100, "adopted": 100,
                  "works": cert.NOT_MEASURED, "safe": cert.NOT_MEASURED}
        self.assertEqual(cert.tier(scores), "🥉 Listed")


class TestCheckIngest(unittest.TestCase):
    def test_missing_field_is_rejected(self):
        import json
        import tempfile
        bad = {"candidates": [{"domain": "tooling", "kind": "repo", "id": "a/b"}]}  # missing url/score/...
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(bad, f)
            path = f.name
        errs = chk.check_candidates("readme text", path)
        os.unlink(path)
        self.assertTrue(any("missing" in e for e in errs))

    def test_missing_file_is_not_a_failure(self):
        # "not measured" ≠ "fail": absent candidates file must not error the gate
        self.assertEqual(chk.check_candidates("readme", "/nonexistent/candidates.json"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
