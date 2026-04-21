"""
Orchestrator — wires Research → Analyst → Critic with optional refinement loop.
Handles per-agent timing, delta computation, and final response assembly.
"""

import time
import uuid
from typing import Optional

from agents.research_agent import ResearchAgent
from agents.analyst_agent  import AnalystAgent
from agents.critic_agent   import CriticAgent
from schemas.models        import ResearchOutput, AnalystOutput, CriticOutput
from utils.logger          import get_logger
from utils.memory          import add_entry

logger          = get_logger("orchestrator")
MAX_ITERATIONS  = 2   # Critic can trigger at most 1 refinement round


class Orchestrator:
    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id or uuid.uuid4().hex[:8]

    async def run(self, query: str, context: Optional[str] = None) -> dict:
        logger.info("[%s] Pipeline START  query='%s'", self.request_id, query[:80])
        t_pipeline = time.time()
        timings: dict[str, float] = {}

        # ── Phase 1: Research ──────────────────────────────────────────────
        t0 = time.time()
        research: ResearchOutput = await ResearchAgent(self.request_id).run(
            query=query, context=context
        )
        timings["research_ms"] = round((time.time() - t0) * 1000, 1)

        # ── Phase 2+3: Analyst → Critic (with optional refinement) ─────────
        iteration      = 1
        prior_issues:  list          = []
        analysis:      Optional[AnalystOutput] = None
        critique:      Optional[CriticOutput]  = None

        while iteration <= MAX_ITERATIONS:
            # Analyst
            t0 = time.time()
            analysis = await AnalystAgent(self.request_id).run(
                query=query,
                research=research,
                iteration=iteration,
                prior_issues=prior_issues,
            )
            timings[f"analyst_iter{iteration}_ms"] = round((time.time() - t0) * 1000, 1)

            # Critic
            t0 = time.time()
            critique = await CriticAgent(self.request_id).run(
                query=query,
                research=research,
                analysis=analysis,
                iteration=iteration,
            )
            timings[f"critic_iter{iteration}_ms"] = round((time.time() - t0) * 1000, 1)

            if critique.needs_refinement and iteration < MAX_ITERATIONS:
                logger.info(
                    "[%s] Refinement triggered — %d issue(s), running iteration %d",
                    self.request_id, len(critique.issues_identified), iteration + 1,
                )
                prior_issues = critique.issues_identified
                iteration   += 1
            else:
                break

        pipeline_ms = round((time.time() - t_pipeline) * 1000, 1)
        result = self._assemble(
            query=query,
            research=research,
            analysis=analysis,
            critique=critique,
            timings=timings,
            iterations=iteration,
            pipeline_ms=pipeline_ms,
        )

        add_entry(query, result, self.request_id)
        logger.info(
            "[%s] Pipeline END  confidence=%s iterations=%d total=%.0fms",
            self.request_id,
            critique.confidence_adjustment,
            iteration,
            pipeline_ms,
        )
        return result

    # ── Private ────────────────────────────────────────────────────────────

    def _assemble(
        self,
        query: str,
        research: ResearchOutput,
        analysis: AnalystOutput,
        critique: CriticOutput,
        timings: dict,
        iterations: int,
        pipeline_ms: float,
    ) -> dict:
        delta = self._delta(analysis, critique)

        return {
            # ── Strict final-output schema ──────────────────────────
            "decision":           critique.final_decision,
            "confidence":         critique.confidence_adjustment,
            "key_reasons":        analysis.insights[:3],
            "recommended_action": analysis.recommendation,

            # ── Detailed agent outputs ──────────────────────────────
            "research_output": {
                "data_points":     research.data_points,
                "context_summary": research.context_summary,
            },
            "analyst_output": {
                "insights":       analysis.insights,
                "risks":          analysis.risks,
                "recommendation": analysis.recommendation,
            },
            "critic_output": {
                "issues_identified":    critique.issues_identified,
                "confidence_adjustment": critique.confidence_adjustment,
                "final_decision":        critique.final_decision,
                "needs_refinement":      critique.needs_refinement,
            },

            # ── Observability meta ──────────────────────────────────
            "_meta": {
                "request_id":           self.request_id,
                "query":                query,
                "iterations":           iterations,
                "refinement_triggered": iterations > 1,
                "delta":                delta,
                "timings_ms":           timings,
                "pipeline_ms":          pipeline_ms,
            },
        }

    @staticmethod
    def _delta(analysis: AnalystOutput, critique: CriticOutput) -> str:
        n = len(critique.issues_identified)
        if n == 0:
            return "no_delta — critic accepted analyst output"
        if n == 1:
            return f"minor_delta — 1 issue: {critique.issues_identified[0][:80]}"
        return (
            f"significant_delta — {n} issues; "
            f"confidence={critique.confidence_adjustment}"
        )
