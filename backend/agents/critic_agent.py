"""
Critic Agent — validates the analysis, adjusts confidence, and writes the final decision.
Sets needs_refinement=True when >= 2 material issues are found (max one refinement round).
"""

import time
from utils.llm    import call_llm, extract_json
from utils.logger import get_logger
from schemas.models import ResearchOutput, AnalystOutput, CriticOutput

logger = get_logger("critic_agent")

SYSTEM_PROMPT = """You are a Critic Agent in a multi-agent AI decision pipeline.

You receive research data AND an analyst's output. Your job:
1. Identify genuine logical flaws, unsupported claims, or missing considerations
2. Assign an honest confidence level
3. Write a comprehensive final decision

You MUST respond with ONLY a valid JSON object — no preamble, no markdown, no explanation:

{
  "issues_identified": [
    "Specific issue 1 (or empty array if none)"
  ],
  "confidence_adjustment": "high",
  "needs_refinement": false,
  "final_decision": "A definitive 2-3 sentence decision that integrates research and analysis."
}

Rules:
- issues_identified: array of SPECIFIC flaws (empty [] if the analysis is solid)
- confidence_adjustment: "high" | "medium" | "low"
    high   = thorough, well-supported, minimal ambiguity
    medium = reasonable but notable gaps or assumptions
    low    = weak, contradictory, or highly uncertain
- needs_refinement: true ONLY if there are 2+ material issues that change the recommendation
- final_decision: definitive, actionable, 2-3 sentences
- Be rigorous — real issues only, no nitpicking
- Output ONLY the JSON object — absolutely nothing else"""


class CriticAgent:
    def __init__(self, request_id: str = "?"):
        self.request_id = request_id

    async def run(
        self,
        query: str,
        research: ResearchOutput,
        analysis: AnalystOutput,
        iteration: int = 1,
    ) -> CriticOutput:
        logger.info(
            "[%s] CriticAgent starting (iteration %d)", self.request_id, iteration
        )
        t0 = time.time()

        prompt = (
            f"Original Query: {query}\n\n"
            f"=== RESEARCH ===\n"
            f"Context: {research.context_summary}\n"
            f"Data Points:\n"
            + "\n".join(f"  {i+1}. {dp}" for i, dp in enumerate(research.data_points))
            + f"\n\n=== ANALYST OUTPUT ===\n"
            f"Insights:\n"
            + "\n".join(f"  {i+1}. {ins}" for i, ins in enumerate(analysis.insights))
            + f"\nRisks:\n"
            + "\n".join(f"  {i+1}. {r}" for i, r in enumerate(analysis.risks))
            + f"\nRecommendation: {analysis.recommendation}\n\n"
            f"Iteration: {iteration}"
            + (
                "\nNote: this is a refinement pass — be especially thorough."
                if iteration > 1 else ""
            )
            + "\n\nProduce the JSON critic output now."
        )

        raw = await call_llm(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3,
            request_id=self.request_id,
        )

        parsed = extract_json(raw, request_id=self.request_id)

        issues     = _to_list(parsed.get("issues_identified", []))
        confidence = str(parsed.get("confidence_adjustment", "medium")).lower()
        if confidence not in ("high", "medium", "low"):
            confidence = "medium"

        needs_ref  = bool(parsed.get("needs_refinement", False))
        final_dec  = str(parsed.get("final_decision", "")).strip()
        if not final_dec:
            raise ValueError("CriticAgent: final_decision is empty")

        # Hard-cap: never loop more than once
        if iteration >= 2:
            needs_ref = False

        result = CriticOutput(
            issues_identified=issues,
            confidence_adjustment=confidence,
            needs_refinement=needs_ref,
            final_decision=final_dec,
        )

        ms = round((time.time() - t0) * 1000, 1)
        logger.info(
            "[%s] CriticAgent done — confidence=%s needs_refinement=%s issues=%d in %.0fms",
            self.request_id, confidence, needs_ref, len(issues), ms,
        )
        return result


def _to_list(val) -> list:
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    return [str(val)] if val else []
