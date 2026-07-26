from pydantic import BaseModel
from typing import Any, Optional
from enum import Enum


class FactParty(str, Enum):
    CARDMEMBER = "cardmember"
    MERCHANT = "merchant"
    TRANSACTION = "transaction"


class AtomicFact(BaseModel):
    """A fact directly observable in a single document - extracted by LLM."""
    fact_id: str
    fact_type: str
    value: Any
    source_doc: str  # doc_id reference
    source_span: str  # the text excerpt that evidences this fact
    party: FactParty
    confidence: float = 1.0


class DerivedFact(BaseModel):
    """A fact computed by comparing multiple atomic facts - pure Python, no LLM."""
    fact_id: str
    fact_type: str
    value: Any
    derived_from: list[str]  # fact_ids consumed
    derivation_rule: str  # human-readable description of the computation
    confidence: float = 1.0
