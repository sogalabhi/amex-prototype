from pydantic import BaseModel


class ClassifiedEvent(BaseModel):
    reason_code: str
    justification: str
    elapsed_ms: int


class FactsExtractedEvent(BaseModel):
    atomic_facts: list[dict]
    derived_facts: list[dict]
    elapsed_ms: int


class RulesFiredEvent(BaseModel):
    fired_rules: list[dict]
    defeated_rules: list[dict]
    raw_score: float
    confidence: float
    elapsed_ms: int


class VerdictEvent(BaseModel):
    verdict: str
    confidence: float
    reason_code: str
    elapsed_ms: int


class MemoEvent(BaseModel):
    merchant_memo: str
    cardmember_memo: str
    elapsed_ms: int


class LedgerEvent(BaseModel):
    chain: list[dict]
    total_elapsed_ms: int


class DoneEvent(BaseModel):
    total_elapsed_ms: int
