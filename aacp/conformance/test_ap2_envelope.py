"""AP-2 Bounded Exposure (行为围栏): CT-2.1 cumulative, CT-2.2 rate."""

from __future__ import annotations

from ..model import DecisionResult
from .base import APResult, CTResult, SUTFactory, make_action, make_grant


def ct_2_1(make_sut: SUTFactory) -> CTResult:
    """Cumulative envelope: aggregate executed amount must never exceed Φ."""
    sut = make_sut()
    grant = make_grant(cumulative_limit=2500.0, rate_limit=0, max_amount_per_action=1000.0)
    sut.reset(grant)
    executed_sum = 0.0
    denied_for_envelope = False
    for _ in range(4):
        d = sut.submit(make_action("ORDER", "merchant_A", 900.0))  # under fresh-consent threshold
        if d.executed:
            executed_sum += d.action.amount
        elif "envelope" in d.basis:
            denied_for_envelope = True
    passed = executed_sum <= 2500.0 and denied_for_envelope
    return CTResult(
        "CT-2.1", "AP-2", "包络边界 / cumulative boundary", passed,
        f"executed_sum={executed_sum} (limit 2500); breach denied={denied_for_envelope}",
        {"executed_sum": executed_sum, "limit": 2500.0, "breach_denied": denied_for_envelope},
    )


def ct_2_2(make_sut: SUTFactory) -> CTResult:
    """Rate envelope: actions beyond rate_limit within the window are blocked."""
    sut = make_sut()
    grant = make_grant(rate_limit=3, rate_window_s=60.0, cumulative_limit=0)
    sut.reset(grant)
    allowed = 0
    rate_denied = False
    for _ in range(5):
        d = sut.submit(make_action("QUERY", "merchant_A", 0.0))
        if d.executed:
            allowed += 1
        elif "rate" in d.basis:
            rate_denied = True
    passed = allowed <= 3 and rate_denied
    return CTResult(
        "CT-2.2", "AP-2", "速率围栏 / rate fence", passed,
        f"allowed={allowed} (limit 3); rate breach denied={rate_denied}",
        {"allowed": allowed, "rate_limit": 3, "rate_denied": rate_denied},
    )


def run(make_sut: SUTFactory) -> APResult:
    return APResult("AP-2", "敞口有界 / Bounded Exposure",
                    [ct_2_1(make_sut), ct_2_2(make_sut)])
