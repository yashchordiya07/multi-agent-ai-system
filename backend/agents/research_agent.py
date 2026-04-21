"""
Research Agent — extracts data_points and context_summary from the query.
Temperature is kept low (0.2) for factual accuracy.
"""

import time
from typing import Optional
from utils.llm    import call_llm, extract_json
from utils.logger import get_logger
from schemas.models import ResearchOutput

logger = get_logger("research_agent")

SYSTEM_PROMPT = """You are a Research Agent in a multi-agent AI decision pipeline.

Your ONLY job is to analyse the user's query and produce structured research data.

You MUST respond with ONLY a valid JSON object — no preamble, no markdown, no explanation:

{
  "data_points": [
    "Specific factual point 1",
    "Specific factual point 2",
    "Specific factual point 3",
    "Specific factual point 4",
    "Specific factual point 5"
  ],
  "context_summary": "A concise 2-3 sentence summary of the core context and background relevant to the query."
}

Rules:
- data_points: array of 4-8 concrete, specific, factual statements (complete sentences)
- context_summary: objective background; NO opinions, NO recommendations
- Output ONLY the JSON object — absolutely nothing else"""


class ResearchAgent:
    def __init__(self, request_id: str = "?"):
        self.request_id = request_id

    async def run(self, query: str, context: Optional[str] = None) -> ResearchOutput:
        logger.info("[%s] ResearchAgent starting", self.request_id)
        t0 = time.time()

        prompt = f"Query: {query}"
        if context:
            prompt += f"\n\nAdditional context: {context}"
        prompt += "\n\nProduce the JSON research output now."

        raw = await call_llm(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.2,
            request_id=self.request_id,
        )

        parsed = extract_json(raw, request_id=self.request_id)

        # Coerce + validate
        data_points = parsed.get("data_points", [])
        if not isinstance(data_points, list):
            data_points = [str(data_points)]
        data_points = [str(p) for p in data_points if str(p).strip()]

        context_summary = str(parsed.get("context_summary", "")).strip()
        if not context_summary:
            raise ValueError("ResearchAgent: context_summary is empty")

        result = ResearchOutput(
            data_points=data_points or ["No data points extracted"],
            context_summary=context_summary,
        )

        ms = round((time.time() - t0) * 1000, 1)
        logger.info(
            "[%s] ResearchAgent done — %d data_points in %.0fms",
            self.request_id, len(result.data_points), ms,
        )
        return result
