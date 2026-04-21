"""
Pydantic v2 schemas — validated at every agent boundary and API layer.
"""

from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator


# ── Request ────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query:   str = Field(..., min_length=3, max_length=2000)
    context: Optional[str] = Field(None, max_length=1000)

    @field_validator("query")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be blank")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "query": "Should our startup adopt microservices or keep a monolith?",
                "context": "5-person team, 8k DAU, Python stack",
            }]
        }
    }


# ── Agent outputs ──────────────────────────────────────────────────────────

class ResearchOutput(BaseModel):
    data_points:     List[str] = Field(..., min_length=1)
    context_summary: str       = Field(..., min_length=10)


class AnalystOutput(BaseModel):
    insights:       List[str] = Field(..., min_length=1)
    risks:          List[str] = Field(..., min_length=1)
    recommendation: str       = Field(..., min_length=10)


class CriticOutput(BaseModel):
    issues_identified:   List[str] = Field(default_factory=list)
    confidence_adjustment: str     = Field(..., pattern=r"^(high|medium|low)$")
    needs_refinement:    bool      = Field(default=False)
    final_decision:      str       = Field(..., min_length=10)


# ── Pipeline meta ──────────────────────────────────────────────────────────

class PipelineMeta(BaseModel):
    request_id:           str
    query:                str
    iterations:           int
    refinement_triggered: bool
    timings_ms:           dict[str, float]
    pipeline_ms:          float
    cached:               bool = False
    delta:                str  = ""


# ── Final API response ─────────────────────────────────────────────────────

class FinalResponse(BaseModel):
    # Top-level decision (strict schema as specified)
    decision:           str
    confidence:         str
    key_reasons:        List[str]
    recommended_action: str

    # Detailed agent outputs
    research_output: dict
    analyst_output:  dict
    critic_output:   dict

    # Observability
    _meta: Optional[Any] = None

    model_config = {"extra": "allow"}


# ── Error ──────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail:     str
    error_type: str = "error"
