"""Pytest wrapper: the bundled reference enforcement point must reach L2 PASS,
and every individual conformance test must pass. Suitable for CI.
"""

from __future__ import annotations

import pytest

from aacp.reference_pea import ReferencePEA
from aacp.runner import run_conformance

_REPORT = run_conformance(make_sut=lambda: ReferencePEA(), sut_name="reference-pea")
_ALL_CTS = [(ap.ap_id, c) for ap in _REPORT.ap_results for c in ap.cts]


def test_reference_reaches_l2():
    assert _REPORT.all_passed, _REPORT.level


@pytest.mark.parametrize("ap_id,ct", _ALL_CTS, ids=[c.ct_id for _, c in _ALL_CTS])
def test_each_conformance_case(ap_id, ct):
    assert ct.passed, f"{ct.ct_id} ({ct.name}) failed: {ct.detail}"
