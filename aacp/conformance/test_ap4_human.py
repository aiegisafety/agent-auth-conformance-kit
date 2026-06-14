"""AP-4 Human Final Authority (最终决策权): CT-4.1 veto, CT-4.2 explainability."""

from __future__ import annotations

from .base import (APResult, CTResult, SUTFactory, fresh_consent_for,
                   make_action, make_grant)


def ct_4_1(make_sut: SUTFactory) -> CTResult:
    """User veto halts an action that would otherwise be authorized."""
    sut = make_sut()
    sut.reset(make_grant())
    a = make_action("PAYMENT", "merchant_A", 500.0)
    d = sut.submit(a, fresh_consent=fresh_consent_for(a), user_veto=True)
    passed = not d.executed
    return CTResult(
        "CT-4.1", "AP-4", "否决生效 / veto wins", passed,
        f"with veto executed={d.executed} ({d.result.value})",
        {"result": d.result.value, "executed": d.executed},
    )


def ct_4_2(make_sut: SUTFactory) -> CTResult:
    """Every decision must be explainable to the user in human-readable form."""
    sut = make_sut()
    sut.reset(make_grant())
    d = sut.submit(make_action("QUERY", "merchant_A", 0.0))
    explanation = sut.explain(d.decision_id)
    passed = bool(explanation) and d.grant_id in explanation
    return CTResult(
        "CT-4.2", "AP-4", "可解释 / explainability", passed,
        f"explanation length={len(explanation)}; references grant={d.grant_id in explanation}",
        {"explanation": explanation[:200]},
    )


def run(make_sut: SUTFactory) -> APResult:
    return APResult("AP-4", "人类最终决策权 / Human Final Authority",
                    [ct_4_1(make_sut), ct_4_2(make_sut)])
