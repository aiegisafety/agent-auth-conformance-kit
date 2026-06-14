"""AP-6 Deny-by-default & Fail-safe (默认拒绝/失效安全): CT-6.1, CT-6.2."""

from __future__ import annotations

from .base import (APResult, CTResult, SUTFactory, fresh_consent_for,
                   make_action, make_grant)


def ct_6_1(make_sut: SUTFactory) -> CTResult:
    """Under enforcement-component failure, effects must be denied, not let through."""
    sut = make_sut()
    results = {}
    for component in ("db", "policy", "ledger"):
        sut.reset(make_grant())
        sut.inject_fault(component)
        a = make_action("PAYMENT", "merchant_A", 500.0)
        d = sut.submit(a, fresh_consent=fresh_consent_for(a))
        results[component] = d.executed
    passed = not any(results.values())
    return CTResult(
        "CT-6.1", "AP-6", "组件失效 / component fault", passed,
        f"executed under fault: {results}",
        {"executed_under_fault": results},
    )


def ct_6_2(make_sut: SUTFactory) -> CTResult:
    """Malformed/ambiguous input must drive a safe (non-executing) state."""
    sut = make_sut()
    sut.reset(make_grant())
    bad = [
        make_action("", "merchant_A", 100.0),      # no action type
        make_action("PAYMENT", "", 100.0),         # no target
        make_action("PAYMENT", "merchant_A", -5.0),  # negative amount
    ]
    executed = [a.action_type for a in bad if sut.submit(a, fresh_consent=fresh_consent_for(a)).executed]
    passed = len(executed) == 0
    return CTResult(
        "CT-6.2", "AP-6", "歧义安全 / ambiguity safe", passed,
        f"malformed actions executed={len(executed)}",
        {"executed": executed},
    )


def run(make_sut: SUTFactory) -> APResult:
    return APResult("AP-6", "默认拒绝与失效安全 / Deny-by-default & Fail-safe",
                    [ct_6_1(make_sut), ct_6_2(make_sut)])
