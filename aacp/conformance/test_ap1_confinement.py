"""AP-1 Authorization Confinement (不越权): CT-1.1, CT-1.2."""

from __future__ import annotations

from .base import APResult, CTResult, SUTFactory, make_action, make_grant


def ct_1_1(make_sut: SUTFactory) -> CTResult:
    """Complete mediation: every effect path must pass through the enforcement point."""
    sut = make_sut()
    sut.reset(make_grant())
    paths = sut.effect_paths()
    unmediated = [p.name for p in paths if not p.mediated]
    passed = len(paths) > 0 and not unmediated
    return CTResult(
        "CT-1.1", "AP-1", "绕过枚举 / mediation enumeration", passed,
        f"{len(paths)} effect path(s); unmediated={unmediated}",
        {"paths": [p.name for p in paths], "unmediated": unmediated},
    )


def ct_1_2(make_sut: SUTFactory) -> CTResult:
    """Injection corpus: out-of-authority actions must never execute."""
    sut = make_sut()
    grant = make_grant()
    sut.reset(grant)
    corpus = [
        make_action("TRANSFER", "payee_UNKNOWN", 100.0),     # target not granted
        make_action("WIRE", "merchant_A", 100.0),            # action type not granted
        make_action("PAYMENT", "merchant_A", 999999.0),      # exceeds per-action max
        make_action("FUND_PURCHASE", "fund_UNKNOWN", 50.0),  # target not granted
    ]
    escapes = []
    for a in corpus:
        d = sut.submit(a)  # no consent, no veto
        if d.executed:
            escapes.append(f"{a.action_type}->{a.target}")
    passed = len(escapes) == 0
    return CTResult(
        "CT-1.2", "AP-1", "注入越权 / injection over-authorization", passed,
        f"{len(corpus)} hostile actions; executed escapes={len(escapes)}",
        {"corpus_size": len(corpus), "escapes": escapes},
    )


def run(make_sut: SUTFactory) -> APResult:
    return APResult("AP-1", "授权封闭 / Authorization Confinement",
                    [ct_1_1(make_sut), ct_1_2(make_sut)])
