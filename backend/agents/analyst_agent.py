"""
Analyst Agent — derives insights, risks, and a recommendation from research.
Supports a refinement pass (iteration > 1) when the Critic flags issues.
"""

import time
from typing import Optional
from utils.llm    import call_llm, extract_json
from utils.logger import get_logger
from schemas.models import ResearchOutput, AnalystOutput

logger = get_logger("analyst_agent")

SYSTEM_PROMPT = """You are an Analyst Agent in a multi-agent AI decision pipeline.

You receive structured research data and produce deep analytical insights.

You MUST respond with ONLY a valid JSON object — no preamble, no markdown, no explanation:

{
  "insights": [
    "Analytical insight 1 derived from the data",
    "Analytical insight 2",
    "Analytical insight 3"
  ],
  "risks": [
    "Risk or concern 1",
    "Risk or concern 2"
  ],
  "recommendation": "A single clear, actionable recommendation sentence."
}

Rules:
- insights: 3-6 analytical observations that go BEYOND restating facts — draw connections, implications, second-order effects
- risks: 2-5 genuine risks, downsides, or uncertainties
- recommendation: ONE specific, actionable sentence
- Output ONLY the JSON object — absolutely nothing else"""


class AnalystAgent:
    def __init__(self, request_id: str = "?"):
        self.request_id = request_id

    async def run(
        self,
        query: str,
        research: ResearchOutput,
        iteration: int = 1,
        prior_issues: Optional[list] = None,
    ) -> AnalystOutput:
        logger.info(
            "[%s] AnalystAgent starting (iteration %d)", self.request_id, iteration
        )
        t0 = time.time()

        prompt = (
            f"Original Query: {query}\n\n"
            f"Research Context Summary:\n{research.context_summary}\n\n"
            f"Research Data Points:\n"
            + "\n".join(f"  {i+1}. {dp}" for i, dp in enumerate(research.data_points))
        )

        if prior_issues and iteration > 1:
            prompt += (
                f"\n\n--- REFINEMENT PASS (Iteration {iteration}) ---\n"
                f"The Critic identified these issues in your previous analysis:\n"
                + "\n".join(f"  • {iss}" for iss in prior_issues)
                + "\nAddress each issue and improve your analysis accordingly."
            )

        prompt += "\n\nProduce the JSON analyst output now."

        raw = await call_llm(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.5,
            request_id=self.request_id,
        )

        parsed = extract_json(raw, request_id=self.request_id)

        insights       = _to_str_list(parsed.get("insights", []))
        risks          = _to_str_list(parsed.get("risks", []))
        recommendation = str(parsed.get("recommendation", "")).strip()

        if not recommendation:
            raise ValueError("AnalystAgent: recommendation is empty")

        result = AnalystOutput(
            insights=insights or ["No insights generated"],
            risks=risks or ["No risks identified"],
            recommendation=recommendation,
        )

        ms = round((time.time() - t0) * 1000, 1)
        logger.info(
            "[%s] AnalystAgent done — %d insights, %d risks in %.0fms",
            self.request_id, len(result.insights), len(result.risks), ms,
        )
        return result


def _to_str_list(val) -> list:
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    return [str(val)] if val else []
