"""AP-5 Tamper-evident Auditability (可追溯): CT-5.1 tamper, CT-5.2 reconstruct."""

from __future__ import annotations

from .base import (APResult, CTResult, SUTFactory, fresh_consent_for,
                   make_action, make_grant)


def _exercise(sut) -> None:
    sut.reset(make_grant())
    sut.submit(make_action("QUERY", "merchant_A", 0.0))
    a = make_action("PAYMENT", "merchant_A", 500.0)
    sut.submit(a, fresh_consent=fresh_consent_for(a))
    sut.submit(make_action("TRANSFER", "payee_UNKNOWN", 100.0))  # denied, still logged


def ct_5_1(make_sut: SUTFactory) -> CTResult:
    """Tampering with any ledger record must be detectable."""
    sut = make_sut()
    _exercise(sut)
    ledger = sut.ledger()
    recs = ledger.records
    if not recs:
        return CTResult(
            "CT-5.1", "AP-5", "防篡改 / tamper detection", False,
            "no ledger records produced - cannot demonstrate tamper-evidence",
            {"records": 0},
        )
    before = ledger.verify()
    recs[0].effect["executed"] = not recs[0].effect["executed"]
    after = ledger.verify()
    passed = before.ok and (not after.ok)
    return CTResult(
        "CT-5.1", "AP-5", "防篡改 / tamper detection", passed,
        f"pre-tamper ok={before.ok}; post-tamper detected={not after.ok} "
        f"(at index {after.broken_index})",
        {"pre_ok": before.ok, "post_ok": after.ok, "broken_index": after.broken_index},
    )


def ct_5_2(make_sut: SUTFactory) -> CTResult:
    """Decisions must be reconstructable from the ledger ALONE."""
    sut = make_sut()
    _exercise(sut)
    narrative = sut.ledger().reconstruct()
    complete = all(
        n.get("who") and n.get("under_grant") and n.get("verdict") is not None
        for n in narrative
    )
    executed = [n for n in narrative if n.get("executed")]
    have_provenance = all(n.get("effect_digest") for n in executed)
    passed = bool(narrative) and complete and have_provenance
    return CTResult(
        "CT-5.2", "AP-5", "仅账本重建 / reconstruct from ledger", passed,
        f"records={len(narrative)}, executed={len(executed)}, complete={complete}, "
        f"provenance={have_provenance}",
        {"records": len(narrative), "executed": len(executed)},
    )


def run(make_sut: SUTFactory) -> APResult:
    return APResult("AP-5", "可追溯审计 / Tamper-evident Auditability",
                    [ct_5_1(make_sut), ct_5_2(make_sut)])
