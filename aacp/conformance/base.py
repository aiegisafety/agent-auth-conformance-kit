"""Shared types and helpers for AACP conformance checks.

A *check* is a callable that takes a SUT factory (returns a fresh, constructed
System Under Test) and returns a CTResult. Checks build their own grants and
reset the SUT, so they are independent and order-free.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from ..model import Action, ConsentToken, DecisionTier, Grant, ReversibilityClass
from ..sut import SystemUnderTest

SUTFactory = Callable[[], SystemUnderTest]


@dataclass
class CTResult:
    ct_id: str
    ap_id: str
    name: str
    passed: bool
    detail: str
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APResult:
    ap_id: str
    title: str
    cts: List[CTResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.cts) and len(self.cts) > 0


# --- builders ---------------------------------------------------------------

def make_grant(**kw: Any) -> Grant:
    base = dict(
        allowed_action_types={"QUERY", "ORDER", "PAYMENT", "FUND_PURCHASE", "TRANSFER"},
        allowed_targets={"merchant_A", "fund_X", "payee_known"},
        max_amount_per_action=2000.0,
        cumulative_limit=5000.0,
        rate_limit=3,
        rate_window_s=60.0,
    )
    base.update(kw)
    return Grant(**base)


def make_action(action_type: str, target: str, amount: float = 0.0, **kw: Any) -> Action:
    return Action(action_type=action_type, target=target, amount=amount, **kw)


def fresh_consent_for(action: Action) -> ConsentToken:
    return ConsentToken(action_id=action.action_id,
                        issued_at=time.time(), expires_at=time.time() + 120)


def expired_consent_for(action: Action) -> ConsentToken:
    return ConsentToken(action_id=action.action_id,
                        issued_at=time.time() - 300, expires_at=time.time() - 180)
