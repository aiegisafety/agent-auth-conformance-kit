"""Core data model for the Agent Authorization Conformance Kit (AACP).

These types are the contract between a System Under Test (SUT) and the
conformance harness. They intentionally mirror the AACP v0.1 specification:
decision tiers (T0/T1/T2), reversibility classes, and authorization results.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Set


class DecisionTier(str, Enum):
    """Decision tiers aligned with the three boundaries in the 实施意见."""

    T0 = "T0"  # 仅限用户本人决策 — agent may prepare, must never execute
    T1 = "T1"  # 需用户授权决策 — execute only within an explicit grant
    T2 = "T2"  # 智能体自主决策 — execute only inside a pre-declared envelope


class ReversibilityClass(str, Enum):
    REVERSIBLE = "REVERSIBLE"
    COMPENSABLE = "COMPENSABLE"
    IRREVERSIBLE = "IRREVERSIBLE"


class DecisionResult(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"  # requires fresh transactional consent / human


def _now() -> float:
    return time.time()


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


@dataclass
class Action:
    """An effectful action the agent intends to perform."""

    action_type: str
    target: str
    amount: float = 0.0
    params: Dict[str, Any] = field(default_factory=dict)
    # Reversibility may be declared by the agent, but the enforcement point
    # is responsible for its own authoritative classification.
    declared_reversibility: Optional[ReversibilityClass] = None
    requested_tier: DecisionTier = DecisionTier.T1
    action_id: str = field(default_factory=lambda: _uid("act"))


@dataclass
class Grant:
    """An explicit authorization issued by the user (the only source of authority)."""

    grant_id: str = field(default_factory=lambda: _uid("grant"))
    allowed_action_types: Set[str] = field(default_factory=set)
    allowed_targets: Set[str] = field(default_factory=set)
    max_amount_per_action: float = 0.0
    cumulative_limit: float = 0.0          # Φ: cumulative amount envelope
    rate_limit: int = 0                    # Φ: max actions per window (0 = unset)
    rate_window_s: float = 60.0
    granted_at: float = field(default_factory=_now)
    expires_at: float = field(default_factory=lambda: _now() + 3600)

    def covers(self, action: "Action", now: Optional[float] = None) -> bool:
        now = now if now is not None else _now()
        if now > self.expires_at:
            return False
        if self.allowed_action_types and action.action_type not in self.allowed_action_types:
            return False
        if self.allowed_targets and action.target not in self.allowed_targets:
            return False
        if self.max_amount_per_action and action.amount > self.max_amount_per_action:
            return False
        return True


@dataclass
class ConsentToken:
    """A fresh, single-use transactional authorization for an irreversible action."""

    token_id: str = field(default_factory=lambda: _uid("consent"))
    action_id: str = ""
    issued_at: float = field(default_factory=_now)
    expires_at: float = field(default_factory=lambda: _now() + 120)

    def is_fresh(self, action: "Action", now: Optional[float] = None) -> bool:
        now = now if now is not None else _now()
        return (
            self.action_id == action.action_id
            and self.issued_at <= now <= self.expires_at
        )


@dataclass
class EnvelopeState:
    metric: str
    used: float
    limit: float
    window_s: float = 0.0


@dataclass
class Decision:
    """The enforcement point's verdict on an action, plus evidence."""

    result: DecisionResult
    action: "Action"
    grant_id: str = ""
    basis: str = ""
    reversibility_class: Optional[ReversibilityClass] = None
    envelope_state: Optional[EnvelopeState] = None
    executed: bool = False
    effect_digest: str = ""
    fresh_consent_token_id: Optional[str] = None
    fail_safe_triggered: bool = False
    decision_id: str = field(default_factory=lambda: _uid("dec"))
    timestamp: float = field(default_factory=_now)

    @property
    def allowed(self) -> bool:
        return self.result == DecisionResult.ALLOW
