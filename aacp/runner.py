"""Conformance runner: drives all AP checks against a SUT and aggregates results."""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import List

from .conformance import (test_ap1_confinement, test_ap2_envelope,
                          test_ap3_irreversible, test_ap4_human,
                          test_ap5_audit, test_ap6_failsafe)
from .conformance.base import APResult, SUTFactory

PROFILE_VERSION = "AACP v0.1"

_AP_MODULES = [
    test_ap1_confinement,
    test_ap2_envelope,
    test_ap3_irreversible,
    test_ap4_human,
    test_ap5_audit,
    test_ap6_failsafe,
]


@dataclass
class ConformanceReport:
    profile_version: str
    sut_name: str
    generated_at: str
    ap_results: List[APResult] = field(default_factory=list)

    @property
    def total_cts(self) -> int:
        return sum(len(ap.cts) for ap in self.ap_results)

    @property
    def passed_cts(self) -> int:
        return sum(1 for ap in self.ap_results for c in ap.cts if c.passed)

    @property
    def all_passed(self) -> bool:
        return all(ap.passed for ap in self.ap_results) and len(self.ap_results) > 0

    @property
    def level(self) -> str:
        # L2 (Tested) is awarded only when every conformance test passes.
        return "L2 — Tested (PASS)" if self.all_passed else "L2 — Tested (FAIL)"


def run_conformance(make_sut: SUTFactory, sut_name: str) -> ConformanceReport:
    results = [mod.run(make_sut) for mod in _AP_MODULES]
    return ConformanceReport(
        profile_version=PROFILE_VERSION,
        sut_name=sut_name,
        generated_at=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        ap_results=results,
    )
