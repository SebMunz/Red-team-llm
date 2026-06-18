from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Callable

from .detectors import detect_findings
from .models import Suite, Technique


@dataclass(frozen=True)
class ManualRunCase:
    technique: Technique
    prompt: str


@dataclass(frozen=True)
class ExecutedCase:
    technique: Technique
    prompt: str
    response: str
    findings: list[str]


def build_manual_cases(
    suite: Suite, techniques: list[Technique], limit: int | None = None
) -> list[ManualRunCase]:
    by_id = {technique.id: technique for technique in techniques}
    cases: list[ManualRunCase] = []
    for technique_id in suite.technique_ids:
        technique = by_id[technique_id]
        prompt = technique.examples[0] if technique.examples else technique.how_to
        cases.append(ManualRunCase(technique=technique, prompt=prompt))
        if limit is not None and len(cases) >= limit:
            break
    return cases


def render_manual_markdown(suite: Suite, cases: list[ManualRunCase]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"# Manual Run: {suite.title}",
        "",
        f"- Suite: `{suite.id}`",
        f"- Generated at: `{now}`",
        "- Mode: manual-first",
        "",
    ]
    for index, case in enumerate(cases, start=1):
        technique = case.technique
        lines.extend(
            [
                f"## {index}. {technique.id} - {technique.title}",
                "",
                f"Family: `{technique.family}`",
                f"Severity hint: `{technique.severity_hint}`",
                "",
                "Prompt:",
                "",
                "```text",
                case.prompt,
                "```",
                "",
                "Expected safe behavior:",
            ]
        )
        lines.extend(f"- {item}" for item in technique.expected_safe_behavior)
        lines.extend(
            [
                "",
                "Result:",
                "",
                "```text",
                "pending",
                "```",
                "",
                "Observed failure:",
                "",
                "```text",
                "pending",
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def run_cases(
    suite: Suite,
    techniques: list[Technique],
    target: Callable[[str], str],
    limit: int | None = None,
) -> list[ExecutedCase]:
    executed: list[ExecutedCase] = []
    for case in build_manual_cases(suite, techniques, limit=limit):
        response = target(case.prompt)
        executed.append(
            ExecutedCase(
                technique=case.technique,
                prompt=case.prompt,
                response=response,
                findings=detect_findings(response),
            )
        )
    return executed


def render_execution_markdown(
    suite: Suite, cases: list[ExecutedCase], target_name: str
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"# Execution Run: {suite.title}",
        "",
        f"- Suite: `{suite.id}`",
        f"- Target: `{target_name}`",
        f"- Generated at: `{now}`",
        f"- Cases: `{len(cases)}`",
        "",
    ]
    for index, case in enumerate(cases, start=1):
        verdict = "needs-review" if case.findings else "no-detector-hit"
        lines.extend(
            [
                f"## {index}. {case.technique.id} - {case.technique.title}",
                "",
                f"Family: `{case.technique.family}`",
                f"Verdict: `{verdict}`",
                "",
                "Prompt:",
                "",
                "```text",
                case.prompt,
                "```",
                "",
                "Response:",
                "",
                "```text",
                case.response,
                "```",
                "",
                "Detector findings:",
                "",
            ]
        )
        if case.findings:
            lines.extend(f"- `{finding}`" for finding in case.findings)
        else:
            lines.append("- none")
        lines.append("")
    return "\n".join(lines)


def write_jsonl_report(
    path: Path, cases: list[ExecutedCase], suite: Suite, target_name: str
) -> None:
    rows = []
    for case in cases:
        rows.append(
            {
                "suite_id": suite.id,
                "target": target_name,
                "technique_id": case.technique.id,
                "technique_title": case.technique.title,
                "family": case.technique.family,
                "prompt": case.prompt,
                "response": case.response,
                "findings": case.findings,
            }
        )
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows),
        encoding="utf-8",
    )
