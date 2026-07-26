"""
Stage 1 — Classification (LLM via OpenRouter)
One OpenRouter call: dispute claim + transaction → reason code + justification.
"""
from schemas.dispute import DisputeCase
from pipeline.openrouter import call_openrouter_json


async def classify_dispute(case: DisputeCase) -> dict:
    """Classify a dispute into an Amex reason code.

    Returns: {"reason_code": "4554", "justification": "..."}
    """
    prompt = f"""You are an expert Amex chargeback classifier. Given a dispute case, identify the single most appropriate Amex reason code.

Available reason codes (choose exactly one):
- 4554: Goods and Services Not Received — Card Member claims non-delivery or partial delivery
- 4553: Not As Described Or Defective Merchandise — goods differ from description or are defective
- 4512: Multiple Processing — same transaction charged multiple times
- 4544: Cancellation Of Recurring Goods / Services — recurring charge after cancellation

TRANSACTION:
  ID: {case.transaction.txn_id}
  Amount: {case.transaction.amount} {case.transaction.currency}
  Date: {case.transaction.date}
  Merchant: {case.transaction.merchant}
  Channel: {case.transaction.channel}

CARDMEMBER CLAIM (filed {case.cardmember_claim.filed_date}):
{case.cardmember_claim.text}

Respond with ONLY valid JSON:
{{"reason_code": "XXXX", "justification": "One sentence explaining why this code applies."}}"""

    return await call_openrouter_json(prompt)
