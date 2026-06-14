"""Negative control: a deliberately insecure SUT must NOT reach L2.

If this ever passes, the conformance suite is vacuous and must be fixed.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aacp.runner import run_conformance
from examples.insecure_sut import InsecureSUT


def test_insecure_sut_fails_l2():
    report = run_conformance(make_sut=lambda: InsecureSUT(), sut_name="insecure-sut")
    assert not report.all_passed, "negative control unexpectedly passed — tests are vacuous"
    # And it should fail on the core authority properties specifically.
    failed = {ap.ap_id for ap in report.ap_results if not ap.passed}
    assert "AP-1" in failed
    assert "AP-3" in failed
