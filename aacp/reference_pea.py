"""Reference enforcement point (a minimal PEA-style broker).

This is a *worked example* of a conforming System Under Test. It is NOT a
production engine; it exists so the conformance kit has something to exercise
and so adopters can see what "passing" looks like. It implements, honestly:

  * Complete mediation + no ambient authority      (AP-1)
  * Continuous effect envelope: cumulative + rate   (AP-2)
  * Reversibility gate w/ fresh transactional consent (AP-3)
  * Soft-auth: user veto wins, system cannot mint authority (AP-4)
  * Hash-chained tamper-evident ledger              (AP-5)
  * Deny-by-default + fail-safe under component fault (AP-6)
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict
from typing import Dict, List, Optional

from .ledger import Ledger, LedgerRecord
from .model import (
    Action,
    ConsentToken,
    Decision,
    DecisionResult,
    DecisionTier,
    EnvelopeState,
    Grant,
    ReversibilityClass,
)
from .sut import EffectPath, SystemUnderTest

# Authoritative reversibility classification by action type.
_REVERSIBILITY = {
    "QUERY": ReversibilityClass.REVERSIBLE,
    "DATA_READ": ReversibilityClass.REVERSIBLE,
    "CART_ADD": ReversibilityClass.REVERSIBLE,
    "ORDER": ReversibilityClass.COMPENSABLE,
    "PAYMENT": ReversibilityClass.IRREVERSIBLE,
    "TRANSFER": ReversibilityClass.IRREVERSIBLE,
    "FUND_PURCHASE": ReversibilityClass.IRREVERSIBLE,
    "CONTRACT_SIGN": ReversibilityClass.IRREVERSIBLE,
    "DATA_SHARE": ReversibilityClass.IRREVERSIBLE,
}


def _digest(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:16]


class ReferencePEA(SystemUnderTest):
    def __init__(self, fresh_consent_threshold: float = 1000.0):
        self.fresh_consent_threshold = fresh_consent_threshold
        self._grant: Optional[Grant] = None
        self._ledger = Ledger()
        self._cum_used = 0.0
        self._action_times: List[float] = []
        self._decisions: Dict[str, Decision] = {}
        self._fault: Optional[str] = None

    # -- lifecycle ---------------------------------------------------------
    def reset(self, grant: Grant) -> None:
        self._grant = grant
        self._ledger = Ledger()
        self._cum_used = 0.0
        self._action_times = []
        self._decisions = {}
        self._fault = None

    def ledger(self) -> Ledger:
        return self._ledger

    def inject_fault(self, component: str) -> None:
        self._fault = component

    def clear_fault(self) -> None:
        self._fault = None

    def effect_paths(self) -> List[EffectPath]:
        # The ONLY route from intent to a resource passes through this broker.
        return [EffectPath("agent -> broker(E) -> resource", mediated=True)]

    def explain(self, decision_id: str) -> str:
        d = self._decisions.get(decision_id)
        if not d:
            return ""
        return (
            f"Decision {d.decision_id}: {d.result.value} for action "
            f"'{d.action.action_type}' on '{d.action.target}' (amount={d.action.amount}). "
            f"Checked against grant '{d.grant_id}'. Basis: {d.basis}. "
            f"Reversibility={d.reversibility_class.value if d.reversibility_class else 'n/a'}."
        )

    def classify(self, action: Action) -> ReversibilityClass:
        return _REVERSIBILITY.get(action.action_type, ReversibilityClass.IRREVERSIBLE)

    # -- core enforcement --------------------------------------------------
    def submit(
        self,
        action: Action,
        fresh_consent: Optional[ConsentToken] = None,
        user_veto: bool = False,
    ) -> Decision:
        now = time.time()
        rev = self.classify(action)

        def finalize(result: DecisionResult, basis: str, executed: bool,
                     fail_safe: bool = False, env: Optional[EnvelopeState] = None,
                     consent_id: Optional[str] = None) -> Decision:
            dec = Decision(
                result=result,
                action=action,
                grant_id=self._grant.grant_id if self._grant else "",
                basis=basis,
                reversibility_class=rev,
                envelope_state=env,
                executed=executed,
                effect_digest=_digest(asdict(action)) if executed else "",
                fresh_consent_token_id=consent_id,
                fail_safe_triggered=fail_safe,
            )
            self._decisions[dec.decision_id] = dec
            self._record(dec, user_veto)
            return dec

        # AP-6: fail-safe. If a required enforcement dependency is down,
        # deny by default rather than letting effects through.
        if self._fault in ("policy", "db", "broker"):
            return finalize(DecisionResult.DENY, f"fail-safe: '{self._fault}' unavailable",
                            executed=False, fail_safe=True)
        if self._fault == "ledger":
            # Cannot produce an audit record -> refuse to act (no silent effects).
            return Decision(
                result=DecisionResult.DENY, action=action,
                grant_id=self._grant.grant_id if self._grant else "",
                basis="fail-safe: ledger unavailable, refusing to execute unauditable effect",
                reversibility_class=rev, executed=False, fail_safe_triggered=True,
            )

        # AP-6: ambiguity / malformed input -> safe state.
        if not action.action_type or not action.target or action.amount < 0:
            return finalize(DecisionResult.DENY, "fail-safe: malformed/ambiguous action",
                            executed=False, fail_safe=True)

        # AP-4: user veto is absolute. The system may block; it cannot mint authority.
        if user_veto:
            return finalize(DecisionResult.DENY, "user veto (human final authority)",
                            executed=False)

        # AP-1: authorization confinement. No ambient authority: every action is
        # explicitly checked against the active grant.
        if self._grant is None or not self._grant.covers(action, now):
            return finalize(DecisionResult.DENY, "outside active grant (AP-1 confinement)",
                            executed=False)

        # AP-3: irreversible / above-threshold actions need fresh transactional consent.
        needs_fresh = rev == ReversibilityClass.IRREVERSIBLE or action.amount > self.fresh_consent_threshold
        if needs_fresh:
            if fresh_consent is None or not fresh_consent.is_fresh(action, now):
                return finalize(DecisionResult.ESCALATE,
                                "irreversible/high-value: requires fresh transactional consent (AP-3)",
                                executed=False)

        # AP-2: continuous effect envelope (cumulative amount + rate).
        env = EnvelopeState(metric="cumulative_amount",
                            used=self._cum_used, limit=self._grant.cumulative_limit,
                            window_s=self._grant.rate_window_s)
        if self._grant.cumulative_limit and (self._cum_used + action.amount) > self._grant.cumulative_limit:
            return finalize(DecisionResult.DENY,
                            "cumulative envelope exceeded (AP-2)", executed=False, env=env)
        if self._grant.rate_limit:
            recent = [t for t in self._action_times if now - t <= self._grant.rate_window_s]
            if len(recent) >= self._grant.rate_limit:
                return finalize(DecisionResult.DENY, "rate envelope exceeded (AP-2)",
                                executed=False, env=env)

        # ALLOW: execute the effect and update envelope counters.
        self._cum_used += action.amount
        self._action_times.append(now)
        env = EnvelopeState(metric="cumulative_amount", used=self._cum_used,
                            limit=self._grant.cumulative_limit, window_s=self._grant.rate_window_s)
        return finalize(DecisionResult.ALLOW, "within grant and envelope", executed=True,
                        env=env, consent_id=(fresh_consent.token_id if fresh_consent else None))

    # -- ledger ------------------------------------------------------------
    def _record(self, dec: Decision, user_veto: bool) -> None:
        rec = LedgerRecord(
            record_id=dec.decision_id,
            timestamp=dec.timestamp,
            principal={"user_id": "user", "agent_id": "agent", "session_id": "s1"},
            decision_tier=dec.action.requested_tier.value,
            intent={
                "action_type": dec.action.action_type,
                "target_resource": dec.action.target,
                "params_digest": _digest({"amount": dec.action.amount, **dec.action.params}),
            },
            grant_ref={
                "grant_id": dec.grant_id,
                "grant_scope_digest": _digest(
                    sorted(self._grant.allowed_action_types) if self._grant else []
                ),
                "granted_at": self._grant.granted_at if self._grant else 0,
                "expires_at": self._grant.expires_at if self._grant else 0,
            },
            authorization={
                "result": dec.result.value,
                "basis": dec.basis,
                "reversibility_class": dec.reversibility_class.value if dec.reversibility_class else None,
                "envelope_state": asdict(dec.envelope_state) if dec.envelope_state else None,
                "fresh_consent_token": dec.fresh_consent_token_id,
            },
            human_in_loop={
                "notice_issued": True,
                "user_decision": "REJECTED" if user_veto else "NONE",
                "veto": user_veto,
            },
            effect={
                "executed": dec.executed,
                "effect_digest": dec.effect_digest,
                "external_ref": f"ref:{dec.decision_id}" if dec.executed else "",
            },
            enforcement={
                "component_id": "reference-pea",
                "policy_version": "aacp-0.1",
                "fail_safe_triggered": dec.fail_safe_triggered,
            },
        )
        self._ledger.append(rec)
