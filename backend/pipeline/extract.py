"""
Stage 2 — Evidence Extraction (LLM via OpenRouter)
Emits ONLY observable atomic facts — things visible in a single document.
Cross-document derived facts are computed by derive.py (pure Python).
"""
import json
import asyncio
from schemas.dispute import DisputeCase, MerchantDocument
from schemas.facts import AtomicFact, FactParty
from pipeline.openrouter import call_openrouter_json

EXTRACTION_SCHEMAS = {
    "order_receipt": {
        "facts_to_extract": {
            "shipping_address_on_order": "string — the shipping address on the order, or null if not stated",
            "order_items": "string — description of items ordered, or null",
            "order_amount": "number — total amount on the receipt, or null",
            "policy_disclosed_at_purchase": "boolean — was a return/cancellation policy mentioned on the receipt, or null if unclear",
            "ticket_number": "string — flight/airline e-ticket number if present (e.g. '081-2244551903'), or null",
            "passenger_name": "string — name of airline passenger if present, or null",
            "booking_reference": "string — airline PNR/booking reference code (e.g. 'KQ7F2M'), or null",
        },
        "party": "merchant",
    },
    "delivery_confirmation": {
        "facts_to_extract": {
            "delivery_status": "string — e.g. 'DELIVERED', 'IN_TRANSIT', 'FAILED', or null",
            "delivery_address": "string — the exact address goods were delivered to, or null",
            "delivery_date": "string — date of delivery, or null",
            "signature_captured": "boolean — was a signature obtained on delivery, or null",
            "recipient_name": "string — name of person who signed or received, or null",
            "ticket_number": "string — e-ticket number referenced in status report, or null",
            "ticket_flown_status": "string — 'FLOWN', 'UNUSED', 'CANCELLED', or null if not airline coupon report",
        },
        "party": "merchant",
    },
    "chat_log": {
        "facts_to_extract": {
            "cardmember_acknowledged_receipt": "boolean — did the customer/cardmember confirm receiving the goods in this conversation, or null",
            "recipient_linked_to_cardmember": "boolean — is there evidence linking the delivery recipient to the cardmember, or null",
            "remedy_offered": "string — what remedy (if any) did the merchant offer, or null if none offered",
            "remedy_type": "string — one of: 'refund', 'exchange', 'credit', 'return', 'repair', or null",
            "return_initiated": "boolean — did the cardmember actually initiate a return, or null",
            "cancellation_notice_date": "string — date the cardmember requested cancellation, or null if not applicable",
        },
        "party": "merchant",
    },
    "policy": {
        "facts_to_extract": {
            "policy_disclosed_at_purchase": "boolean — true if a return/cancellation policy is documented here",
        },
        "party": "merchant",
    },
    "product_description": {
        "facts_to_extract": {
            "product_description_stated": "string — the written product description at time of purchase, or null",
            "variation_disclaimer": "string — any disclaimer about natural variation, colour differences, etc., or null if none",
        },
        "party": "merchant",
    },
    "merchant_photos": {
        "facts_to_extract": {
            "description_photos_match": "boolean — do the merchant's photos generally match the product description, or null if unclear",
        },
        "party": "merchant",
    },
}


async def extract_from_document(
    doc: MerchantDocument, case_id: str, reason_code: str
) -> list[AtomicFact]:
    """Extract atomic facts from a single merchant evidence document."""
    schema = EXTRACTION_SCHEMAS.get(doc.type.value)
    if not schema:
        return []

    facts_spec = json.dumps(schema["facts_to_extract"], indent=2)

    prompt = f"""You are an evidence analyst extracting facts from a dispute document.
This dispute is classified under Amex reason code {reason_code}.

DOCUMENT ID: {doc.doc_id}
DOCUMENT TYPE: {doc.type.value}
DOCUMENT CONTENT:
---
{doc.content}
---

Extract the following facts from this document. For each fact, provide:
- "value": the extracted value (use the exact type specified)
- "source_span": the exact text excerpt from the document that evidences this fact

If a fact is NOT present or cannot be determined from this document, set its value to null and source_span to "".
Do NOT guess or fabricate — if uncertain, use null.

Facts to extract:
{facts_spec}

Respond with ONLY valid JSON in this exact format:
{{
  "fact_name_1": {{"value": ..., "source_span": "..."}},
  "fact_name_2": {{"value": ..., "source_span": "..."}}
}}"""

    raw = await call_openrouter_json(prompt)
    facts = []
    party = FactParty(schema["party"])

    for fact_type, extraction in raw.items():
        if isinstance(extraction, dict) and extraction.get("value") is not None:
            facts.append(
                AtomicFact(
                    fact_id=f"F-{case_id}-{doc.doc_id}-{fact_type}",
                    fact_type=fact_type,
                    value=extraction["value"],
                    source_doc=doc.doc_id,
                    source_span=extraction.get("source_span", ""),
                    party=party,
                    confidence=1.0,
                )
            )

    return facts


async def extract_from_cardmember_claim(case: DisputeCase, reason_code: str) -> list[AtomicFact]:
    """Extract atomic facts from the cardmember's claim text."""
    prompt = f"""You are an evidence analyst extracting facts from a cardmember's dispute claim.
This dispute is classified under Amex reason code {reason_code}.

CARDMEMBER CLAIM (filed {case.cardmember_claim.filed_date}):
---
{case.cardmember_claim.text}
---

Extract the following facts. For each, provide value and the exact source_span from the claim text.
If a fact is NOT present or cannot be determined, set value to null and source_span to "".

Facts to extract:
- "defect_claimed_specific": boolean — does the cardmember describe a specific, concrete physical defect (not just general dissatisfaction)?
- "defect_description": string — what exactly does the cardmember claim is wrong with the goods?
- "attribute_contradiction_claimed": boolean — does the cardmember explicitly claim a specific stated product attribute (e.g. material, colour, dimensions from the listing) contradicts what they received?

Respond with ONLY valid JSON:
{{
  "defect_claimed_specific": {{"value": ..., "source_span": "..."}},
  "defect_description": {{"value": ..., "source_span": "..."}},
  "attribute_contradiction_claimed": {{"value": ..., "source_span": "..."}}
}}"""

    raw = await call_openrouter_json(prompt)
    facts = []

    for fact_type, extraction in raw.items():
        if isinstance(extraction, dict) and extraction.get("value") is not None:
            facts.append(
                AtomicFact(
                    fact_id=f"F-{case.case_id}-CLAIM-{fact_type}",
                    fact_type=fact_type,
                    value=extraction["value"],
                    source_doc="CARDMEMBER_CLAIM",
                    source_span=extraction.get("source_span", ""),
                    party=FactParty.CARDMEMBER,
                    confidence=1.0,
                )
            )

    return facts


def extract_from_transaction(case: DisputeCase) -> list[AtomicFact]:
    """Extract facts directly from the structured transaction record (no LLM needed)."""
    facts = []

    if case.transaction.shipping_address_on_order:
        facts.append(
            AtomicFact(
                fact_id=f"F-{case.case_id}-TXN-shipping_address_on_order",
                fact_type="shipping_address_on_order",
                value=case.transaction.shipping_address_on_order,
                source_doc="TRANSACTION",
                source_span=case.transaction.shipping_address_on_order,
                party=FactParty.TRANSACTION,
                confidence=1.0,
            )
        )

    facts.append(
        AtomicFact(
            fact_id=f"F-{case.case_id}-TXN-billing_date",
            fact_type="billing_date",
            value=case.transaction.date,
            source_doc="TRANSACTION",
            source_span=case.transaction.date,
            party=FactParty.TRANSACTION,
            confidence=1.0,
        )
    )

    facts.append(
        AtomicFact(
            fact_id=f"F-{case.case_id}-TXN-order_amount",
            fact_type="order_amount",
            value=case.transaction.amount,
            source_doc="TRANSACTION",
            source_span=str(case.transaction.amount),
            party=FactParty.TRANSACTION,
            confidence=1.0,
        )
    )

    return facts


async def extract_all_facts(case: DisputeCase, reason_code: str) -> list[AtomicFact]:
    """Run extraction across all sources using OpenRouter."""
    transaction_facts = extract_from_transaction(case)
    claim_facts = await extract_from_cardmember_claim(case, reason_code)

    doc_facts = []
    for doc in case.merchant_evidence:
        facts = await extract_from_document(doc, case.case_id, reason_code)
        doc_facts.extend(facts)

    all_facts = list(transaction_facts) + claim_facts + doc_facts
    return all_facts
