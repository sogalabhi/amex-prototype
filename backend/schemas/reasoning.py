from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Verdict(str, Enum):
    CARDMEMBER = "CARDMEMBER"
    MERCHANT = "MERCHANT"
    ESCALATE_HUMAN_REVIEW = "ESCALATE_HUMAN_REVIEW"
    NOT_CHARGEABLE_UNDER_CODE = "NOT_CHARGEABLE_UNDER_CODE"


class FiredRule(BaseModel):
    rule_id: str
    weight: float
    original_weight: float
    consumed_fact_ids: list[str]
    rulebook_text: Optional[str] = None
    defeated: bool = False
    defeated_by: Optional[str] = None


class ReasoningResult(BaseModel):
    verdict: Verdict
    reason_code: str
    confidence: float
    raw_score: float
    fired_rules: list[FiredRule]
    exclusion_applied: Optional[dict] = None
    all_facts: list[dict]
