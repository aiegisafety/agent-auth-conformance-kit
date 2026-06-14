"""System-Under-Test (SUT) adapter interface.

To run the conformance kit against your own agent + enforcement point,
implement this interface. The kit drives it through the AACP v0.1 test
cases (CT-1.1 .. CT-6.2) and produces an L2 conformance report.

The kit never trusts the agent's intent; it only observes the SUT's
DECISIONS and the resulting LEDGER. A conforming SUT is one whose
enforcement makes out-of-authority effects impossible to execute.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .ledger import Ledger
from .model import Action, ConsentToken, Decision, Grant


class SystemUnderTest(ABC):
    """The contract an adopter implements to be tested for AACP conformance."""

    @abstractmethod
    def reset(self, grant: Grant) -> None:
        """Start a fresh session governed by `grant`."""

    @abstractmethod
    def submit(
        self,
        action: Action,
        fresh_consent: Optional[ConsentToken] = None,
        user_veto: bool = False,
    ) -> Decision:
        """Submit an effectful action through the enforcement point and return its decision."""

    @abstractmethod
    def ledger(self) -> Ledger:
        """Return the tamper-evident authorization ledger for the session."""

    @abstractmethod
    def effect_paths(self) -> List["EffectPath"]:
        """Enumerate every path by which an effect can reach a resource (AP-1 / CT-1.1)."""

    @abstractmethod
    def explain(self, decision_id: str) -> str:
        """Return a human-readable explanation for a past decision (AP-4 / CT-4.2)."""

    @abstractmethod
    def inject_fault(self, component: str) -> None:
        """Disable an enforcement dependency to test fail-safe behaviour (AP-6 / CT-6.1)."""

    @abstractmethod
    def clear_fault(self) -> None:
        """Restore normal operation."""


class EffectPath:
    """A route from agent intent to an external effect."""

    def __init__(self, name: str, mediated: bool):
        self.name = name
        self.mediated = mediated

    def __repr__(self) -> str:
        return f"EffectPath(name={self.name!r}, mediated={self.mediated})"
