"""Tamper-evident, append-only, hash-chained authorization ledger (AP-5).

Each record commits to the previous record's hash, so any modification,
reordering, or deletion is detectable by re-walking the chain.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

GENESIS_HASH = "0" * 64


def canonical(obj: Dict[str, Any]) -> str:
    """Deterministic JSON encoding used for hashing."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class LedgerRecord:
    record_id: str
    timestamp: float
    principal: Dict[str, Any]
    decision_tier: str
    intent: Dict[str, Any]
    grant_ref: Dict[str, Any]
    authorization: Dict[str, Any]
    human_in_loop: Dict[str, Any]
    effect: Dict[str, Any]
    enforcement: Dict[str, Any]
    prev_hash: str = GENESIS_HASH
    hash: str = ""

    def payload(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("hash", None)
        return d

    def compute_hash(self) -> str:
        return _sha256(canonical(self.payload()))


class Ledger:
    """Append-only hash chain."""

    def __init__(self) -> None:
        self._records: List[LedgerRecord] = []

    def __len__(self) -> int:
        return len(self._records)

    @property
    def records(self) -> List[LedgerRecord]:
        return list(self._records)

    def head_hash(self) -> str:
        return self._records[-1].hash if self._records else GENESIS_HASH

    def append(self, record: LedgerRecord) -> LedgerRecord:
        record.prev_hash = self.head_hash()
        record.hash = record.compute_hash()
        self._records.append(record)
        return record

    def verify(self) -> "VerificationResult":
        prev = GENESIS_HASH
        for idx, rec in enumerate(self._records):
            if rec.prev_hash != prev:
                return VerificationResult(False, idx, "broken chain link (prev_hash mismatch)")
            if rec.compute_hash() != rec.hash:
                return VerificationResult(False, idx, "record content does not match its hash")
            prev = rec.hash
        return VerificationResult(True, -1, "chain intact")

    def to_json(self) -> str:
        return json.dumps([asdict(r) for r in self._records], ensure_ascii=False, indent=2)

    def reconstruct(self) -> List[Dict[str, Any]]:
        """Rebuild the decision narrative using ONLY the ledger (AP-5 / CT-5.2)."""
        out = []
        for r in self._records:
            out.append(
                {
                    "who": r.principal,
                    "under_grant": r.grant_ref.get("grant_id"),
                    "intended": r.intent,
                    "verdict": r.authorization.get("result"),
                    "executed": r.effect.get("executed"),
                    "effect_digest": r.effect.get("effect_digest"),
                }
            )
        return out


@dataclass
class VerificationResult:
    ok: bool
    broken_index: int
    detail: str
