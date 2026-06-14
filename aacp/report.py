"""Render an L2 conformance report (Markdown + JSON) from a ConformanceReport."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict

from .runner import ConformanceReport


def to_dict(report: ConformanceReport) -> Dict[str, Any]:
    return {
        "profile_version": report.profile_version,
        "sut_name": report.sut_name,
        "generated_at": report.generated_at,
        "conformance_level": report.level,
        "all_passed": report.all_passed,
        "summary": {"total": report.total_cts, "passed": report.passed_cts},
        "properties": [
            {
                "ap_id": ap.ap_id,
                "title": ap.title,
                "passed": ap.passed,
                "tests": [asdict(c) for c in ap.cts],
            }
            for ap in report.ap_results
        ],
    }


def to_json(report: ConformanceReport) -> str:
    return json.dumps(to_dict(report), ensure_ascii=False, indent=2)


def to_markdown(report: ConformanceReport) -> str:
    badge = "✅ PASS" if report.all_passed else "❌ FAIL"
    lines = [
        "# AACP L2 符合性报告 / Conformance Report",
        "",
        f"- **规范 / Profile**: {report.profile_version}",
        f"- **被测系统 / SUT**: `{report.sut_name}`",
        f"- **生成时间 / Generated**: {report.generated_at}",
        f"- **符合性等级 / Level**: **{report.level}**",
        f"- **结论 / Result**: {badge}  ({report.passed_cts}/{report.total_cts} 用例通过)",
        "",
        "> L2「可测量」要求全部符合性用例通过；任一失败即判 L2 FAIL。",
        "",
        "## 属性结果 / Property results",
        "",
        "| 属性 AP | 名称 | 结论 |",
        "|---|---|---|",
    ]
    for ap in report.ap_results:
        lines.append(f"| {ap.ap_id} | {ap.title} | {'✅' if ap.passed else '❌'} |")
    lines += ["", "## 用例明细 / Test detail", ""]
    for ap in report.ap_results:
        lines.append(f"### {ap.ap_id} — {ap.title}")
        lines.append("")
        lines.append("| 用例 | 名称 | 结论 | 说明 |")
        lines.append("|---|---|---|---|")
        for c in ap.cts:
            mark = "✅" if c.passed else "❌"
            lines.append(f"| {c.ct_id} | {c.name} | {mark} | {c.detail} |")
        lines.append("")
    lines += [
        "## 证据 / Evidence (machine-readable)",
        "",
        "完整逐用例证据见 `L2_report.json`；防篡改账本可由 `Ledger.verify()` 独立复核。",
        "",
        "---",
        "*由 agent-auth-conformance-kit 自动生成。本报告对应 AACP 符合性等级 L2（可测量）。"
        "L3（可审计）需附独立第三方对账本的验证报告。*",
    ]
    return "\n".join(lines)
