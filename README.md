# Agent Authorization Conformance Kit (AACP)

[![conformance](https://github.com/aiegisafety/agent-auth-conformance-kit/actions/workflows/conformance.yml/badge.svg)](https://github.com/aiegisafety/agent-auth-conformance-kit/actions/workflows/conformance.yml)

A small, runnable conformance suite for the **Agent Authorization Conformance
Profile (AACP v0.1)** — an open, testable answer to one question regulators and
risk teams are now asking of AI agents that move money, place orders, or share
data:

> **Can you prove the agent never acts outside the user's authorization?**

The kit turns that question into **12 executable test cases** across **6
authorization properties**, run against *your* agent + enforcement point, and
emits a machine- and human-readable **L2 conformance report**.

It does **not** test whether a model is "aligned" or whether the agent's intent
is correct. It assumes the agent may be wrong or manipulated, and checks that the
**enforcement layer makes out-of-authority effects impossible to execute** — and
that every decision is auditable.

> Status: **v0.1, draft for community review.** The profile is published under
> CC-BY-4.0; this reference kit under Apache-2.0. See [`docs/AACP_v0.1.md`](docs/AACP_v0.1.md).

## Why this exists

China's three-ministry *《智能体规范应用与创新发展实施意见》* (May 2026) requires that
an agent "must not exceed the scope of user authorization," that users retain
"the right to know and the final decision," and that operations be "traceable" —
and calls for a *trusted certification standard system* and third-party
assessment. The policy mandate exists; an operational, testable conformance
standard does not yet. This kit is a candidate reference for that gap.

## The six properties

| AP | Property | What it guarantees |
|----|----------|--------------------|
| **AP-1** | Authorization Confinement (不越权) | No effect outside the active grant; complete mediation, no ambient authority |
| **AP-2** | Bounded Exposure (行为围栏) | Aggregate effect stays inside a declared envelope (cumulative + rate) |
| **AP-3** | Irreversible-Action Gate | Irreversible/high-value actions need fresh transactional consent |
| **AP-4** | Human Final Authority | User veto wins; every decision is explainable |
| **AP-5** | Tamper-evident Auditability | Hash-chained ledger; tampering detectable; decisions reconstructable |
| **AP-6** | Deny-by-default & Fail-safe | Under failure/ambiguity the default is *deny*, not execute |

The 12 cases (CT-1.1 … CT-6.2) are defined in [`docs/AACP_v0.1.md`](docs/AACP_v0.1.md) §8.

## Quickstart

```bash
# Python 3.10+
python examples/run_reference.py
```

This runs the kit against the bundled **reference enforcement point** and writes
[`reports/L2_report.md`](reports/L2_report.md) and `reports/L2_report.json`.
Exit code is `0` only if every case passes.

## Test your own system

Implement `aacp.sut.SystemUnderTest` for your agent + enforcement point:

```python
from aacp import run_conformance
from aacp.report import to_markdown

class MySUT(SystemUnderTest):
    ...  # wire your broker / policy engine / ledger

report = run_conformance(make_sut=lambda: MySUT(), sut_name="my-agent")
print(to_markdown(report))   # -> L2 — Tested (PASS|FAIL)
```

A conforming system reaches **L2 — Tested (PASS)** when all 12 cases pass.

## Conformance levels

| Level | Name | Bar |
|-------|------|-----|
| **L1** | Declared | Properties documented; single mediation point; no bypass paths |
| **L2** | Tested | **This kit passes**: 0 injection escapes, envelope + gate demonstrated |
| **L3** | Audited | Tamper-evident ledger + independent third-party verification |

## Tests / CI

```bash
pip install pytest
pytest -q
```

The suite includes a **negative control** (`examples/insecure_sut.py`): a
deliberately insecure agent that the kit must flag as failing. If it ever passes,
the conformance tests are vacuous. CI runs both.

## License & citation

- Reference implementation: **Apache-2.0** (`LICENSE`).
- Profile / specification text: **CC-BY-4.0**.
- Maintained by **AIEGIS**. Spec author: **Aron**.

If you use AACP in research or compliance work, cite *Agent Authorization
Conformance Profile v0.1, AIEGIS, 2026*.
