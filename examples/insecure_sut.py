"""A deliberately NON-conforming SUT, used as a negative control.

It blindly executes whatever the agent intends (ambient authority, no envelope,
no irreversibility gate, ignores veto, no explanation, no fail-safe). The kit
MUST flag it as failing — this proves the conformance tests have teeth.
"""

from __future__ import annotations

from typing import List, Optional

from aacp.ledger import Ledger, LedgerRecord
from aacp.model import (Action, ConsentToken, Decision, DecisionResult,
                        ReversibilityClass)
from aacp.sut import EffectPath, SystemUnderTest


class InsecureSUT(SystemUnderTest):
    def __init__(self) -> None:
        self._ledger = Ledger()

    def reset(self, grant) -> None:
        self._ledger = Ledger()

    def submit(self, action: Action, fresh_consent: Optional[ConsentToken] = None,
               user_veto: bool = False) -> Decision:
        # Executes everything. No checks at all.
        return Decision(result=DecisionResult.ALLOW, action=action, basis="ambient (insecure)",
                        reversibility_class=ReversibilityClass.IRREVERSIBLE,
                        executed=True, effect_digest="x")

    def ledger(self) -> Ledger:
        return self._ledger

    def effect_paths(self) -> List[EffectPath]:
        # A direct, unmediated path to the resource exists -> CT-1.1 must fail.
        return [EffectPath("agent -> resource (DIRECT, unmediated)", mediated=False)]

    def explain(self, decision_id: str) -> str:
        return ""  # no explanation -> CT-4.2 must fail

    def inject_fault(self, component: str) -> None:
        pass  # ignores faults -> CT-6.1 must fail

    def clear_fault(self) -> None:
        pass
