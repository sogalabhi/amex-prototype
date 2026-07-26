"""
Local SHA-256 Hash Chain - tamper-evidence layer.

After each pipeline stage, computes SHA-256(previous_hash + stage_name + payload).
Demonstrates the immutability concept without requiring blockchain infrastructure.
"""
import hashlib
import json
from datetime import datetime, timezone


class LocalChain:
    """In-memory hash chain for dispute resolution audit trails."""

    def __init__(self):
        self._chains: dict[str, list[dict]] = {}  # case_id → chain entries

    def _compute_hash(self, previous_hash: str, stage: str, payload: str) -> str:
        """Compute SHA-256(previous_hash + stage + payload)."""
        data = f"{previous_hash}:{stage}:{payload}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def append(self, case_id: str, stage: str, payload: dict) -> dict:
        """Append a new entry to the chain for a given case.

        Returns the new chain entry.
        """
        if case_id not in self._chains:
            self._chains[case_id] = []

        chain = self._chains[case_id]
        previous_hash = chain[-1]["hash"] if chain else "0" * 64

        payload_json = json.dumps(payload, sort_keys=True, default=str)
        new_hash = self._compute_hash(previous_hash, stage, payload_json)

        entry = {
            "index": len(chain),
            "stage": stage,
            "hash": new_hash,
            "previous_hash": previous_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload_summary": _summarize_payload(stage, payload),
        }

        chain.append(entry)
        return entry

    def get_chain(self, case_id: str) -> list[dict]:
        """Get the full chain for a case."""
        return self._chains.get(case_id, [])

    def verify(self, case_id: str) -> bool:
        """Verify chain integrity - each hash must link to the previous."""
        chain = self._chains.get(case_id, [])
        if not chain:
            return True

        for i, entry in enumerate(chain):
            if i == 0:
                if entry["previous_hash"] != "0" * 64:
                    return False
            else:
                if entry["previous_hash"] != chain[i - 1]["hash"]:
                    return False

        return True


def _summarize_payload(stage: str, payload: dict) -> str:
    """Create a human-readable summary of a stage payload."""
    summaries = {
        "evidence_ingested": lambda p: f"{p.get('document_count', '?')} documents ingested",
        "classified": lambda p: f"Reason code {p.get('reason_code', '?')}: {p.get('justification', '')[:80]}",
        "facts_extracted": lambda p: f"{p.get('atomic_count', '?')} atomic + {p.get('derived_count', '?')} derived facts",
        "rules_fired": lambda p: f"{p.get('rule_count', '?')} rules fired, raw score {p.get('raw_score', '?')}",
        "verdict": lambda p: f"{p.get('verdict', '?')} (confidence {p.get('confidence', '?')})",
        "memo_generated": lambda p: "Decision memos generated (merchant + cardmember views)",
    }

    summarizer = summaries.get(stage, lambda p: json.dumps(p, default=str)[:100])
    try:
        return summarizer(payload)
    except Exception:
        return f"Stage: {stage}"


# Singleton instance - shared across the application
ledger = LocalChain()
