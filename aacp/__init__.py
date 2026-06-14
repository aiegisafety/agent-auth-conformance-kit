"""Agent Authorization Conformance Kit (AACP).

A runnable conformance suite for the Agent Authorization Conformance Profile
(AACP v0.1). Implement `aacp.sut.SystemUnderTest` for your agent + enforcement
point, run the conformance harness, and obtain an L2 (Tested) report.
"""

from .runner import ConformanceReport, run_conformance
from .sut import EffectPath, SystemUnderTest

__all__ = ["run_conformance", "ConformanceReport", "SystemUnderTest", "EffectPath"]
__version__ = "0.1.0"
