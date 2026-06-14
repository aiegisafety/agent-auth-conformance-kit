"""Run the conformance kit against the bundled reference enforcement point
and write an L2 report to ./reports/.

Usage:
    python -m examples.run_reference
    # or
    python examples/run_reference.py
"""

from __future__ import annotations

import os
import sys

# Allow running as a plain script (python examples/run_reference.py).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aacp.reference_pea import ReferencePEA
from aacp.report import to_json, to_markdown
from aacp.runner import run_conformance


def main() -> int:
    report = run_conformance(make_sut=lambda: ReferencePEA(), sut_name="reference-pea")

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "L2_report.md"), "w", encoding="utf-8") as f:
        f.write(to_markdown(report))
    with open(os.path.join(out_dir, "L2_report.json"), "w", encoding="utf-8") as f:
        f.write(to_json(report))

    print(to_markdown(report))
    print()
    print(f"Conformance level: {report.level}")
    return 0 if report.all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
