"""
API Routes - FastAPI endpoints for the dispute resolution system.

GET /api/cases           - list available cases
GET /api/cases/{id}      - full case bundle
GET /api/disputes/{id}/resolve  - SSE stream of pipeline resolution
GET /api/disputes/{id}/ledger   - hash chain for a resolved case
"""
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from schemas.dispute import DisputeCase
from pipeline.resolve import load_case, resolve_dispute_stream
from ledger.local_chain import ledger

router = APIRouter(prefix="/api")

CASES_DIR = Path(__file__).parent.parent / "cases"


def _list_case_files() -> list[str]:
    """List available case names from the cases/ directory."""
    return sorted(
        f.stem for f in CASES_DIR.glob("*.json")
    )


@router.get("/cases")
async def list_cases():
    """List all available dispute cases with summaries."""
    cases = []
    for name in _list_case_files():
        try:
            case = load_case(name)
            cases.append({
                "case_id": case.case_id,
                "case_name": name,
                "merchant": case.transaction.merchant,
                "amount": case.transaction.amount,
                "currency": case.transaction.currency,
                "date": case.transaction.date,
                "claim_summary": case.cardmember_claim.text[:120] + "..."
                    if len(case.cardmember_claim.text) > 120
                    else case.cardmember_claim.text,
                "document_count": len(case.merchant_evidence),
            })
        except Exception:
            continue
    return {"cases": cases}


@router.get("/cases/{case_name}")
async def get_case(case_name: str):
    """Get full case bundle (excluding ground_truth)."""
    try:
        case = load_case(case_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Case '{case_name}' not found")

    # Return without ground_truth - judges shouldn't see expected outcomes
    data = case.model_dump()
    data.pop("ground_truth", None)
    return data


@router.get("/disputes/{case_name}/resolve")
async def resolve_dispute(case_name: str):
    """Stream the pipeline resolution as Server-Sent Events."""
    try:
        case = load_case(case_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Case '{case_name}' not found")

    async def event_generator():
        async for event in resolve_dispute_stream(case):
            yield event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering if proxied
        },
    )


@router.get("/disputes/{case_name}/ledger")
async def get_ledger(case_name: str):
    """Get the hash chain for a previously resolved case."""
    try:
        case = load_case(case_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Case '{case_name}' not found")

    chain = ledger.get_chain(case.case_id)
    if not chain:
        raise HTTPException(
            status_code=404,
            detail=f"No ledger entries for case '{case_name}'. Resolve the case first."
        )

    return {
        "case_id": case.case_id,
        "chain": chain,
        "chain_valid": ledger.verify(case.case_id),
    }
