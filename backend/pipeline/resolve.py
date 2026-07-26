"""
Pipeline Orchestrator - SSE streaming + CLI

Runs the full pipeline: classify → extract → derive → score → explain → ledger
Yields SSE events at each stage with elapsed_ms timing.

Usage:
  CLI:   python -m pipeline.resolve case_a
  API:   StreamingResponse(resolve_dispute_stream(case), media_type="text/event-stream")
"""
import asyncio
import json
import logging
import sys
import time
from pathlib import Path

from schemas.dispute import DisputeCase
from schemas.facts import AtomicFact, DerivedFact
from pipeline.classify import classify_dispute
from pipeline.extract import extract_all_facts
from pipeline.derive import derive_facts
from pipeline.score import score_dispute
from pipeline.explain import generate_memos
from ledger.local_chain import ledger
import config

logger = logging.getLogger("verdict_chain")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def load_case(case_name: str) -> DisputeCase:
    """Load a case from the cases/ directory."""
    cases_dir = Path(__file__).parent.parent / "cases"
    case_file = cases_dir / f"{case_name}.json"
    if not case_file.exists():
        raise FileNotFoundError(f"Case not found: {case_file}")
    with open(case_file) as f:
        data = json.load(f)
    return DisputeCase(**data)


def _sse_event(event_type: str, data: dict) -> str:
    """Format an SSE event string."""
    json_data = json.dumps(data, default=str)
    return f"event: {event_type}\ndata: {json_data}\n\n"


async def resolve_dispute_stream(case: DisputeCase):
    """Run the full pipeline as an async generator, yielding SSE events.

    Each event includes elapsed_ms since pipeline start.
    """
    start = time.monotonic()

    def elapsed_ms() -> int:
        return int((time.monotonic() - start) * 1000)

    # --- Stage 0: Evidence Ingested (ledger entry) ---
    ledger.append(case.case_id, "evidence_ingested", {
        "document_count": len(case.merchant_evidence),
        "case_id": case.case_id,
    })

    # --- Stage 1: Classification ---
    logger.info(f"[{case.case_id}] Starting Stage 1: Classification...")
    classification = await classify_dispute(case)
    reason_code = classification["reason_code"]
    justification = classification.get("justification", "")
    logger.info(f"[{case.case_id}] Classified as Reason Code {reason_code}")

    ledger.append(case.case_id, "classified", {
        "reason_code": reason_code,
        "justification": justification,
    })

    yield _sse_event("classified", {
        "reason_code": reason_code,
        "justification": justification,
        "elapsed_ms": elapsed_ms(),
    })

    # --- Stage 2: Extraction (atomic facts) ---
    logger.info(f"[{case.case_id}] Starting Stage 2: Fact Extraction...")
    atomic_facts = await extract_all_facts(case, reason_code)

    # --- Stage 3: Derivation (cross-document facts) ---
    logger.info(f"[{case.case_id}] Starting Stage 3: Fact Derivation...")
    derived_facts = derive_facts(atomic_facts, case)

    all_facts = list(atomic_facts) + list(derived_facts)
    logger.info(f"[{case.case_id}] Extracted {len(atomic_facts)} atomic facts & {len(derived_facts)} derived facts")

    ledger.append(case.case_id, "facts_extracted", {
        "atomic_count": len(atomic_facts),
        "derived_count": len(derived_facts),
    })

    yield _sse_event("facts_extracted", {
        "atomic_facts": [f.model_dump() for f in atomic_facts],
        "derived_facts": [f.model_dump() for f in derived_facts],
        "elapsed_ms": elapsed_ms(),
    })

    # --- Stage 4: Scoring ---
    reasoning = score_dispute(reason_code, all_facts)

    ledger.append(case.case_id, "rules_fired", {
        "rule_count": len(reasoning.fired_rules),
        "raw_score": reasoning.raw_score,
    })

    fired_dicts = [r.model_dump() for r in reasoning.fired_rules if not r.defeated]
    defeated_dicts = [r.model_dump() for r in reasoning.fired_rules if r.defeated]

    yield _sse_event("rules_fired", {
        "fired_rules": fired_dicts,
        "defeated_rules": defeated_dicts,
        "raw_score": round(reasoning.raw_score, 4),
        "confidence": round(reasoning.confidence, 4),
        "elapsed_ms": elapsed_ms(),
    })

    # --- Verdict ---
    ledger.append(case.case_id, "verdict", {
        "verdict": reasoning.verdict.value,
        "confidence": round(reasoning.confidence, 4),
    })

    yield _sse_event("verdict", {
        "verdict": reasoning.verdict.value,
        "confidence": round(reasoning.confidence, 4),
        "reason_code": reason_code,
        "elapsed_ms": elapsed_ms(),
    })

    # --- Stage 5: Memo generation ---
    memos = await generate_memos(reasoning)

    ledger.append(case.case_id, "memo_generated", {
        "has_merchant_memo": bool(memos.get("merchant_memo")),
        "has_cardmember_memo": bool(memos.get("cardmember_memo")),
    })

    yield _sse_event("memo", {
        "merchant_memo": memos.get("merchant_memo", ""),
        "cardmember_memo": memos.get("cardmember_memo", ""),
        "elapsed_ms": elapsed_ms(),
    })

    # --- Stage 6: Ledger & Commitment ---
    chain = ledger.get_chain(case.case_id)
    total_ms = elapsed_ms()

    evm_receipt = None
    if config.LEDGER_MODE == "evm":
        from ledger.evm_chain import evm_ledger
        evm_receipt = await evm_ledger.commit_verdict_hash(case.case_id, {
            "verdict": reasoning.verdict.value,
            "reason_code": reason_code,
            "raw_score": reasoning.raw_score,
            "confidence": reasoning.confidence,
        })

    yield _sse_event("ledger", {
        "chain": chain,
        "evm": evm_receipt,
        "total_elapsed_ms": total_ms,
    })

    yield _sse_event("done", {
        "total_elapsed_ms": total_ms,
    })


# --- CLI entrypoint ---
async def _run_cli(case_name: str):
    """Run a case from the command line and print results."""
    print(f"\n{'='*60}")
    print(f"  VERDICT CHAIN - Resolving {case_name}")
    print(f"{'='*60}\n")

    case = load_case(case_name)
    print(f"Case: {case.case_id}")
    print(f"Merchant: {case.transaction.merchant}")
    print(f"Amount: {case.transaction.amount} {case.transaction.currency}")
    print(f"Claim: {case.cardmember_claim.text[:80]}...")
    print()

    async for event_str in resolve_dispute_stream(case):
        # Parse the SSE event
        lines = event_str.strip().split("\n")
        event_type = ""
        event_data = {}
        for line in lines:
            if line.startswith("event: "):
                event_type = line[7:]
            elif line.startswith("data: "):
                event_data = json.loads(line[6:])

        if event_type == "classified":
            print(f"[{event_data['elapsed_ms']}ms] ✓ CLASSIFIED: Reason Code {event_data['reason_code']}")
            print(f"  Justification: {event_data['justification']}")
            print()

        elif event_type == "facts_extracted":
            n_atomic = len(event_data.get("atomic_facts", []))
            n_derived = len(event_data.get("derived_facts", []))
            print(f"[{event_data['elapsed_ms']}ms] ✓ FACTS EXTRACTED: {n_atomic} atomic + {n_derived} derived")
            for f in event_data.get("atomic_facts", []):
                print(f"  [{f['fact_id']}] {f['fact_type']} = {f['value']} (from {f['source_doc']})")
            for f in event_data.get("derived_facts", []):
                print(f"  [{f['fact_id']}] {f['fact_type']} = {f['value']} ← DERIVED: {f['derivation_rule'][:60]}")
            print()

        elif event_type == "rules_fired":
            print(f"[{event_data['elapsed_ms']}ms] ✓ RULES FIRED:")
            for r in event_data.get("fired_rules", []):
                print(f"  {r['rule_id']}  {r['weight']:+.2f}  consumed: {r['consumed_fact_ids']}")
            for r in event_data.get("defeated_rules", []):
                print(f"  {r['rule_id']}  {r['original_weight']:+.2f}  ██ DEFEATED by {r['defeated_by']}")
            print(f"  Raw score: {event_data['raw_score']}")
            print(f"  Confidence: {event_data['confidence']}")
            print()

        elif event_type == "verdict":
            verdict = event_data["verdict"]
            conf = event_data["confidence"]
            emoji = {"CARDMEMBER": "🟢", "MERCHANT": "🟠", "ESCALATE_HUMAN_REVIEW": "🟣"}.get(verdict, "⚪")
            print(f"[{event_data['elapsed_ms']}ms] {emoji} VERDICT: {verdict}")
            print(f"  Confidence: {conf:.1%}")
            print()

        elif event_type == "memo":
            print(f"[{event_data['elapsed_ms']}ms] ✓ MEMOS GENERATED")
            print(f"\n--- MERCHANT VIEW ---")
            print(event_data.get("merchant_memo", "(none)")[:500])
            print(f"\n--- CARDMEMBER VIEW ---")
            print(event_data.get("cardmember_memo", "(none)")[:500])
            print()

        elif event_type == "ledger":
            print(f"[{event_data['total_elapsed_ms']}ms] ✓ LEDGER CHAIN:")
            for entry in event_data.get("chain", []):
                print(f"  [{entry['index']}] {entry['stage']}: {entry['hash'][:16]}...")
            print()

        elif event_type == "done":
            total = event_data["total_elapsed_ms"]
            print(f"{'='*60}")
            print(f"  ✅ RESOLVED IN {total/1000:.1f}s")
            print(f"{'='*60}\n")

    # Ground truth check
    if case.ground_truth:
        print(f"GROUND TRUTH: {case.ground_truth.expected_outcome}")
        print(f"REASON: {case.ground_truth.why}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m pipeline.resolve <case_name>")
        print("  e.g.: python -m pipeline.resolve case_a")
        sys.exit(1)

    case_name = sys.argv[1]
    asyncio.run(_run_cli(case_name))
