"""AP-3 Irreversible-Action Gate (不可逆动作闸): CT-3.1, CT-3.2."""

from __future__ import annotations

from ..model import DecisionResult
from .base import (APResult, CTResult, SUTFactory, expired_consent_for,
                   fresh_consent_for, make_action, make_grant)


def ct_3_1(make_sut: SUTFactory) -> CTResult:
    """Irreversible action: denied without fresh consent, allowed with it."""
    sut = make_sut()
    sut.reset(make_grant())
    a1 = make_action("PAYMENT", "merchant_A", 500.0)
    d_without = sut.submit(a1)  # no fresh consent
    a2 = make_action("PAYMENT", "merchant_A", 500.0)
    d_with = sut.submit(a2, fresh_consent=fresh_consent_for(a2))
    passed = (not d_without.executed) and d_with.executed
    return CTResult(
        "CT-3.1", "AP-3", "不可逆闸 / irreversible gate", passed,
        f"no-consent executed={d_without.executed} ({d_without.result.value}); "
        f"with-consent executed={d_with.executed}",
        {"without_consent": d_without.result.value, "with_consent": d_with.result.value},
    )


def ct_3_2(make_sut: SUTFactory) -> CTResult:
    """Expired transactional token must not authorize an irreversible action."""
    sut = make_sut()
    sut.reset(make_grant())
    a = make_action("FUND_PURCHASE", "fund_X", 800.0)
    d = sut.submit(a, fresh_consent=expired_consent_for(a))
    passed = not d.executed
    return CTResult(
        "CT-3.2", "AP-3", "令牌新鲜度 / token freshness", passed,
        f"expired-token executed={d.executed} ({d.result.value})",
        {"result": d.result.value, "executed": d.executed},
    )


def run(make_sut: SUTFactory) -> APResult:
    return APResult("AP-3", "不可逆动作闸 / Irreversible-Action Gate",
                    [ct_3_1(make_sut), ct_3_2(make_sut)])
