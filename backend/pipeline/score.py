"""
Stage 4 - Deterministic Scoring Engine (pure Python, no LLM)

Loads the rules file, matches facts against rule conditions, applies weights
with defeater suppression, and computes normalized confidence.

Key design decisions:
  - Uses `requires_fact` for merchant defenses, `condition` for cardmember conditions (Point #1)
  - Defeaters are hard suppression (weight → 0), not subtraction
  - Confidence = abs(raw_score) / sum(abs(all_applicable_weights_including_defeated))
  - Denominator includes defeated weights for meaningful confidence spread
"""
import json
from pathlib import Path

from schemas.facts import AtomicFact, DerivedFact
from schemas.reasoning import FiredRule, ReasoningResult, Verdict
from config import CONFIDENCE_THRESHOLD


def load_rules() -> dict:
    """Load the Amex reason codes rules file."""
    rules_path = Path(__file__).parent.parent / "rules" / "amex_reason_codes.json"
    with open(rules_path) as f:
        return json.load(f)


def _find_matching_facts(
    fact_type: str, all_facts: list[AtomicFact | DerivedFact]
) -> list[str]:
    """Find all fact_ids that match a given fact_type."""
    matching = []
    for f in all_facts:
        if f.fact_type == fact_type and f.value is not None:
            # For boolean facts, only match if True
            if isinstance(f.value, bool) and not f.value:
                continue
            matching.append(f.fact_id)
    return matching


def score_dispute(
    reason_code: str, all_facts: list[AtomicFact | DerivedFact]
) -> ReasoningResult:
    """Score a dispute using the rules engine.

    Returns a ReasoningResult with verdict, confidence, and fired rules.
    """
    rules = load_rules()
    code_rules = rules.get(reason_code)
    if not code_rules:
        raise ValueError(f"Unknown reason code: {reason_code}")

    fired_rules: list[FiredRule] = []
    defeaters = code_rules.get("defeaters", [])

    # Build a set of active defeater conditions (fact_types that are present)
    active_defeater_facts = set()
    for defeater in defeaters:
        when_fact = defeater["when"]
        if _find_matching_facts(when_fact, all_facts):
            active_defeater_facts.add(defeater["defeats"])

    # --- Process merchant defenses ---
    for defense in code_rules.get("merchant_defenses", []):
        rule_id = defense["id"]
        # Point #1: merchant defenses use "requires_fact"
        fact_key = defense.get("requires_fact") or defense.get("condition")
        if not fact_key:
            continue

        matching_fact_ids = _find_matching_facts(fact_key, all_facts)
        if not matching_fact_ids:
            continue  # Rule doesn't fire - no matching fact

        weight = defense["weight"]
        defeated = rule_id in active_defeater_facts

        # Find which fact triggered the defeat
        defeated_by = None
        if defeated:
            for defeater in defeaters:
                if defeater["defeats"] == rule_id:
                    defeater_fact_ids = _find_matching_facts(defeater["when"], all_facts)
                    if defeater_fact_ids:
                        defeated_by = defeater_fact_ids[0]
                        break

        fired_rules.append(
            FiredRule(
                rule_id=rule_id,
                weight=0.0 if defeated else weight,
                original_weight=weight,
                consumed_fact_ids=matching_fact_ids,
                rulebook_text=defense.get("rulebook_text"),
                defeated=defeated,
                defeated_by=defeated_by,
            )
        )

    # --- Process cardmember conditions ---
    for condition in code_rules.get("cardmember_conditions", []):
        rule_id = condition["id"]
        # Point #1: cardmember conditions use "condition"
        fact_key = condition.get("condition") or condition.get("requires_fact")
        if not fact_key:
            continue

        matching_fact_ids = _find_matching_facts(fact_key, all_facts)
        if not matching_fact_ids:
            continue  # Condition doesn't fire

        weight = condition["weight"]

        fired_rules.append(
            FiredRule(
                rule_id=rule_id,
                weight=weight,
                original_weight=weight,
                consumed_fact_ids=matching_fact_ids,
                rulebook_text=condition.get("rationale", condition.get("rulebook_text")),
                defeated=False,
                defeated_by=None,
            )
        )

    # --- Compute score and confidence ---
    # Raw score: sum of non-defeated weights
    non_defeated_weights = [r.weight for r in fired_rules if not r.defeated]
    raw_score = sum(non_defeated_weights)

    # Denominator: sum of absolute values of ALL applicable weights (including defeated)
    # This makes confidence reflect "how much of the available evidence pointed one way"
    all_applicable_weights = [r.original_weight for r in fired_rules]
    denom = sum(abs(w) for w in all_applicable_weights) or 1.0

    confidence = min(abs(raw_score) / denom, 1.0)

    # Determine verdict
    if confidence < CONFIDENCE_THRESHOLD:
        verdict = Verdict.ESCALATE_HUMAN_REVIEW
    elif raw_score > 0:
        verdict = Verdict.CARDMEMBER
    else:
        verdict = Verdict.MERCHANT

    # Serialize all facts for the reasoning result
    all_facts_dicts = [f.model_dump() for f in all_facts]

    return ReasoningResult(
        verdict=verdict,
        reason_code=reason_code,
        confidence=confidence,
        raw_score=raw_score,
        fired_rules=fired_rules,
        all_facts=all_facts_dicts,
    )
