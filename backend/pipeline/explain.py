"""
Stage 5 — Decision Memo Generation (LLM via OpenRouter)
Generates merchant-facing and cardmember-facing memos from the reasoning object.
"""
import json
from schemas.reasoning import ReasoningResult
from pipeline.openrouter import call_openrouter_json


async def generate_memos(reasoning: ReasoningResult) -> dict:
    """Generate merchant-facing and cardmember-facing decision memos.

    Returns: {"merchant_memo": "...", "cardmember_memo": "..."}
    """
    fired_summary = []
    for rule in reasoning.fired_rules:
        status = "DEFEATED" if rule.defeated else "ACTIVE"
        fired_summary.append({
            "rule_id": rule.rule_id,
            "weight": rule.original_weight,
            "effective_weight": rule.weight,
            "status": status,
            "rulebook_text": rule.rulebook_text,
            "consumed_fact_ids": rule.consumed_fact_ids,
            "defeated_by": rule.defeated_by,
        })

    consumed_ids = set()
    for rule in reasoning.fired_rules:
        consumed_ids.update(rule.consumed_fact_ids)
        if rule.defeated_by:
            consumed_ids.add(rule.defeated_by)

    relevant_facts = [f for f in reasoning.all_facts if f.get("fact_id") in consumed_ids]

    reasoning_data = {
        "verdict": reasoning.verdict.value,
        "reason_code": reasoning.reason_code,
        "confidence": round(reasoning.confidence, 4),
        "raw_score": round(reasoning.raw_score, 4),
        "fired_rules": fired_summary,
        "relevant_facts": relevant_facts,
    }

    confidence_pct = round(reasoning.confidence * 100, 1)
    confidence_framing = (
        f"Confidence reflects the share of applicable evidence supporting the verdict — "
        f"in this case, {confidence_pct}% of weighted evidence points to this outcome."
    )

    prompt = f"""You are writing an official dispute resolution decision memo. You have access ONLY to the following reasoning data. Do NOT introduce any information not present in this data.

REASONING DATA:
{json.dumps(reasoning_data, indent=2)}

CONFIDENCE NOTE: {confidence_framing}

Generate TWO versions of the memo in a single JSON response:

1. "merchant_memo": Addressed to the merchant. Professional, clear.
   - State the verdict and reason code
   - For each ACTIVE fired rule, quote the exact rulebook_text and explain which facts (by fact_id) supported it
   - For each DEFEATED rule, explain why it was defeated and which fact caused the defeat
   - State the confidence level with the framing note above
   - Provide next steps (if merchant lost: appeal rights, additional evidence that could help; if merchant won: resolution timeline)

2. "cardmember_memo": Addressed to the cardmember. Professional, empathetic, clear.
   - State the verdict and reason code in plain language
   - Explain which evidence supported the decision, citing fact_ids
   - For DEFEATED rules, explain in plain terms why the merchant's defense didn't hold
   - State the confidence level
   - Provide next steps (if cardmember lost: what to do next; if cardmember won: when to expect the credit)

For ESCALATED verdicts (ESCALATE_HUMAN_REVIEW):
   - Both memos should explain that the automated system determined the evidence was insufficient for a definitive resolution
   - Describe what additional documentation from each party would help resolve the case
   - Note that the case has been forwarded to a human reviewer with all evidence assembled

CRITICAL RULES:
- Use ONLY facts from the reasoning data — never fabricate
- Quote rulebook_text exactly as provided
- Cite fact_ids when referencing evidence
- Both memos must contain the same factual content, just different framing
- Keep each memo under 500 words
- Use markdown formatting (headers, bold, bullet points)

Respond with ONLY valid JSON:
{{"merchant_memo": "...", "cardmember_memo": "..."}}"""

    return await call_openrouter_json(prompt)
