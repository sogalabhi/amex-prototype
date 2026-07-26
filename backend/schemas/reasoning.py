from pydantic import BaseModel
from typing import Optional
from enum import Enum


class Verdict(str, Enum):
    CARDMEMBER = "CARDMEMBER"
    MERCHANT = "MERCHANT"
    ESCALATE_HUMAN_REVIEW = "ESCALATE_HUMAN_REVIEW"


class FiredRule(BaseModel):
    rule_id: str
    weight: float  # actual weight applied (0 if defeated)
    original_weight: float  # weight before defeat suppression
    consumed_fact_ids: list[str]
    rulebook_text: Optional[str] = None
    defeated: bool = False
    defeated_by: Optional[str] = None  # fact_id that triggered the defeater


class ReasoningResult(BaseModel):
    verdict: Verdict
    reason_code: str
    confidence: float  # normalized: abs(raw) / sum(abs(all applicable weights incl. defeated))
    raw_score: float
    fired_rules: list[FiredRule]  # rules that matched facts (includes defeated ones)
    all_facts: list[dict]  # mixed AtomicFact and DerivedFact dicts
