"""
Stage 3 - Cross-Document Fact Derivation (pure Python, no LLM)

Takes atomic facts from extract.py and computes derived facts that require
comparing multiple documents. This is the architectural keystone:
  - AI reads (extract.py)
  - Python derives (this file)
  - Python decides (score.py)
"The AI never decides anything - it only reads."
"""
import re
from schemas.facts import AtomicFact, DerivedFact
from schemas.dispute import DisputeCase


def normalize_address(addr: str) -> str:
    """Normalize an address for comparison.

    Strips apartment/unit info, expands abbreviations, lowercases, removes punctuation.
    Returns a string suitable for street-level comparison.
    """
    if not addr:
        return ""
    addr = addr.lower().strip()
    # Expand common abbreviations
    abbreviations = [
        (r"\bst\b", "street"),
        (r"\bave\b", "avenue"),
        (r"\brd\b", "road"),
        (r"\bdr\b", "drive"),
        (r"\bln\b", "lane"),
        (r"\bct\b", "court"),
        (r"\bpl\b", "place"),
        (r"\bblvd\b", "boulevard"),
        (r"\bcres\b", "crescent"),
        (r"\btce\b", "terrace"),
    ]
    for abbr, full in abbreviations:
        addr = re.sub(abbr, full, addr)
    # Strip apartment/unit/suite
    addr = re.sub(r",?\s*(apt|unit|suite|ste|flat)\s*\S+", "", addr, flags=re.IGNORECASE)
    # Strip punctuation
    addr = re.sub(r"[^\w\s]", "", addr)
    # Collapse whitespace
    return " ".join(addr.split())


def _get_fact_value(facts: list[AtomicFact], fact_type: str, default=None):
    """Get the value of the first atomic fact matching fact_type."""
    for f in facts:
        if f.fact_type == fact_type and f.value is not None:
            return f.value
    return default


def _get_fact(facts: list[AtomicFact], fact_type: str) -> AtomicFact | None:
    """Get the first atomic fact matching fact_type."""
    for f in facts:
        if f.fact_type == fact_type and f.value is not None:
            return f
    return None


def _get_fact_ids(facts: list[AtomicFact], *fact_types: str) -> list[str]:
    """Get fact_ids for all facts matching any of the given types."""
    return [f.fact_id for f in facts if f.fact_type in fact_types and f.value is not None]


def derive_facts(atomic_facts: list[AtomicFact], case: DisputeCase) -> list[DerivedFact]:
    """Compute cross-document derived facts from atomic facts.

    Each derivation is a pure Python computation - no LLM calls.
    """
    derived = []
    counter = 0

    def _add(fact_type: str, value, derived_from: list[str], rule: str, confidence: float = 1.0):
        nonlocal counter
        counter += 1
        derived.append(
            DerivedFact(
                fact_id=f"D-{case.case_id}-{counter:03d}",
                fact_type=fact_type,
                value=value,
                derived_from=derived_from,
                derivation_rule=rule,
                confidence=confidence,
            )
        )

    # --- Address comparison (4554) ---
    delivery_addr = _get_fact_value(atomic_facts, "delivery_address")
    shipping_addr = _get_fact_value(atomic_facts, "shipping_address_on_order")

    if delivery_addr and shipping_addr:
        norm_delivery = normalize_address(delivery_addr)
        norm_shipping = normalize_address(shipping_addr)
        addrs_match = norm_delivery == norm_shipping

        source_ids = _get_fact_ids(atomic_facts, "delivery_address", "shipping_address_on_order")

        # Always emit delivered_to_cardmember_specified_address so D2 fires
        # (and gets defeated if addresses mismatch). This keeps D2 in the
        # denominator for a meaningful confidence spread.
        _add(
            "delivered_to_cardmember_specified_address",
            True,  # Merchant claims delivery - the defeater handles mismatch
            source_ids,
            f"Delivery evidence present. Normalized: '{norm_delivery}' vs '{norm_shipping}' → {'MATCH' if addrs_match else 'MISMATCH'}",
        )

        if not addrs_match:
            _add(
                "delivery_address_mismatch",
                True,
                source_ids,
                f"Normalized addresses differ: '{norm_delivery}' != '{norm_shipping}'",
            )

    # --- Signature + recipient link (4554) ---
    sig_captured = _get_fact_value(atomic_facts, "signature_captured")
    recipient_link = _get_fact_value(atomic_facts, "recipient_linked_to_cardmember")

    if sig_captured is False and not recipient_link:
        source_ids = _get_fact_ids(atomic_facts, "signature_captured", "recipient_linked_to_cardmember")
        if not source_ids:
            source_ids = _get_fact_ids(atomic_facts, "signature_captured")
        _add(
            "no_signature_and_no_recipient_link",
            True,
            source_ids,
            "No signature captured AND no evidence linking recipient to cardmember",
        )

    # --- Goods received in entirety (4554-D1) ---
    delivery_status = _get_fact_value(atomic_facts, "delivery_status")
    cm_acknowledged = _get_fact_value(atomic_facts, "cardmember_acknowledged_receipt")

    if delivery_status and "deliver" in str(delivery_status).lower():
        # Needs address match AND (signature OR acknowledgement)
        delivery_addr_val = _get_fact_value(atomic_facts, "delivery_address")
        shipping_addr_val = _get_fact_value(atomic_facts, "shipping_address_on_order")

        addr_ok = False
        if delivery_addr_val and shipping_addr_val:
            addr_ok = normalize_address(delivery_addr_val) == normalize_address(shipping_addr_val)

        receipt_confirmed = sig_captured is True or cm_acknowledged is True

        if addr_ok and receipt_confirmed:
            source_ids = _get_fact_ids(
                atomic_facts,
                "delivery_status", "delivery_address", "shipping_address_on_order",
                "signature_captured", "cardmember_acknowledged_receipt",
            )
            _add(
                "goods_received_in_entirety",
                True,
                source_ids,
                "Delivered + address matches + (signature captured OR cardmember acknowledged receipt)",
            )

    # --- Link between recipient and cardmember (4554-D5) ---
    if recipient_link is True or cm_acknowledged is True:
        source_ids = _get_fact_ids(
            atomic_facts, "recipient_linked_to_cardmember", "cardmember_acknowledged_receipt"
        )
        _add(
            "link_between_recipient_and_cardmember",
            True,
            source_ids,
            "Recipient linked to cardmember OR cardmember acknowledged receipt",
        )

    # --- Description match refutes claim (4553-D1) ---
    photos_match = _get_fact_value(atomic_facts, "description_photos_match")
    defect_specific = _get_fact_value(atomic_facts, "defect_claimed_specific")

    if photos_match is True and not defect_specific:
        source_ids = _get_fact_ids(atomic_facts, "description_photos_match", "defect_claimed_specific")
        _add(
            "description_match_refutes_claim",
            True,
            source_ids,
            "Photos match description AND no specific defect claimed",
        )

    # --- Return policy disclosed and not followed (4553-D3) ---
    policy_disclosed = _get_fact_value(atomic_facts, "policy_disclosed_at_purchase")
    return_initiated = _get_fact_value(atomic_facts, "return_initiated")

    if policy_disclosed is True and return_initiated is not True:
        source_ids = _get_fact_ids(atomic_facts, "policy_disclosed_at_purchase", "return_initiated")
        _add(
            "return_policy_disclosed_and_not_followed",
            True,
            source_ids,
            "Return policy was disclosed at purchase AND cardmember did not initiate a return",
        )

    # --- Repair or replacement attempted (4553-D2) ---
    remedy = _get_fact_value(atomic_facts, "remedy_offered")
    remedy_type = _get_fact_value(atomic_facts, "remedy_type")

    if remedy is not None:
        valid_types = {"refund", "exchange", "credit", "return", "repair"}
        if remedy_type and remedy_type.lower() in valid_types:
            source_ids = _get_fact_ids(atomic_facts, "remedy_offered", "remedy_type")
            _add(
                "repair_or_replacement_attempted",
                True,
                source_ids,
                f"Merchant offered remedy: {remedy} (type: {remedy_type})",
            )

    # --- Specific defect not covered by disclosure (4553-C2, defeats D1 and D5) ---
    variation_disclaimer = _get_fact_value(atomic_facts, "variation_disclaimer")

    if defect_specific is True and variation_disclaimer is not None:
        source_ids = _get_fact_ids(atomic_facts, "defect_claimed_specific", "variation_disclaimer")
        _add(
            "specific_defect_not_covered_by_disclosure",
            True,
            source_ids,
            "Cardmember claims a specific physical defect, but merchant's disclaimer is a general variation notice that does not address specific defects",
        )

    # --- Material attribute mismatch (4553-C3) ---
    attr_contradiction = _get_fact_value(atomic_facts, "attribute_contradiction_claimed")

    if attr_contradiction is True:
        source_ids = _get_fact_ids(atomic_facts, "attribute_contradiction_claimed")
        _add(
            "material_attribute_mismatch_vs_written_description",
            True,
            source_ids,
            "Cardmember claims a stated product attribute contradicts what was received (assessed at extraction time)",
        )

    # --- Remedy offered but materially inadequate (4553-C4) ---
    if remedy is not None:
        # Check if the cardmember rejected the remedy (we know from chat context)
        # If remedy was offered and return not initiated but dispute filed, it was inadequate
        if return_initiated is not True:
            source_ids = _get_fact_ids(atomic_facts, "remedy_offered", "return_initiated")
            _add(
                "remedy_offered_but_materially_inadequate",
                True,
                source_ids,
                "Remedy offered but cardmember did not accept (return not initiated, dispute filed instead)",
                confidence=0.8,
            )

    # --- Compelling evidence description matched (4553-D5) ---
    if photos_match is True:
        source_ids = _get_fact_ids(atomic_facts, "description_photos_match")
        _add(
            "compelling_evidence_description_matched",
            True,
            source_ids,
            "Merchant photos generally match the product description",
        )

    # --- Offsetting credit processed (multiple codes) ---
    credit_processed = _get_fact_value(atomic_facts, "credit_already_processed")
    if credit_processed is True:
        source_ids = _get_fact_ids(atomic_facts, "credit_already_processed")
        _add(
            "offsetting_credit_processed",
            True,
            source_ids,
            "A correcting transaction has already been processed",
        )

    # --- Cancellation notice precedes billing date (4544) ---
    cancel_date = _get_fact_value(atomic_facts, "cancellation_notice_date")
    billing_date = _get_fact_value(atomic_facts, "billing_date")

    if cancel_date and billing_date:
        # Simple string comparison works for ISO dates; for other formats, parse
        try:
            from datetime import datetime
            cancel_dt = datetime.fromisoformat(cancel_date)
            billing_dt = datetime.fromisoformat(billing_date)
            if cancel_dt < billing_dt:
                source_ids = _get_fact_ids(atomic_facts, "cancellation_notice_date", "billing_date")
                _add(
                    "cancellation_notice_precedes_billing_date",
                    True,
                    source_ids,
                    f"Cancellation notice ({cancel_date}) precedes billing date ({billing_date})",
                )
        except (ValueError, TypeError):
            pass

    # --- No merchant evidence within response window (all codes, weight 1.00) ---
    if len(case.merchant_evidence) == 0:
        _add(
            "no_merchant_evidence_within_response_window",
            True,
            [],
            "Merchant submitted no evidence documents within the response window",
        )

    return derived
