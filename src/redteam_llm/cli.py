from __future__ import annotations

import argparse
from pathlib import Path

from .catalog import (
    list_suites,
    load_catalog,
    load_suite,
    validate_catalog,
    validate_suite,
)
from .mutators import MUTATORS
from .paths import REPORTS_DIR
from .runner import (
    build_manual_cases,
    render_execution_markdown,
    render_manual_markdown,
    run_cases,
    write_jsonl_report,
)
from .targets import post_json_target, safe_mock_target, vulnerable_mock_target


def _catalog_command(args: argparse.Namespace) -> int:
    techniques = load_catalog()
    if args.catalog_action == "validate":
        result = validate_catalog(techniques)
        for warning in result.warnings:
            print(f"WARN: {warning}")
        for error in result.errors:
            print(f"ERROR: {error}")
        print(f"Catalog techniques: {len(techniques)}")
        print("Catalog status: ok" if result.ok else "Catalog status: failed")
        return 0 if result.ok else 1

    if args.catalog_action == "list":
        rows = techniques
        if args.family:
            rows = [technique for technique in rows if technique.family == args.family]
        if args.tag:
            rows = [technique for technique in rows if args.tag in technique.tags]
        for technique in rows:
            print(f"{technique.id}\t{technique.family}\t{technique.title}")
        return 0

    return 2


def _suite_command(args: argparse.Namespace) -> int:
    techniques = load_catalog()
    if args.suite_action == "list":
        for suite in list_suites():
            result = validate_suite(suite, techniques)
            status = "ok" if result.ok else "invalid"
            print(f"{suite.id}\t{len(suite.technique_ids)} techniques\t{status}")
        return 0

    if args.suite_action == "show":
        suite = load_suite(args.suite)
        by_id = {technique.id: technique for technique in techniques}
        print(f"{suite.id}: {suite.title}")
        print(suite.description)
        for technique_id in suite.technique_ids:
            technique = by_id.get(technique_id)
            title = technique.title if technique else "UNKNOWN"
            print(f"- {technique_id}: {title}")
        return 0

    return 2


def _load_validated_suite(args: argparse.Namespace):
    techniques = load_catalog()
    suite = load_suite(args.suite)
    validation = validate_suite(suite, techniques)
    if not validation.ok:
        for error in validation.errors:
            print(f"ERROR: {error}")
        return None, None
    return techniques, suite


def _run_manual_command(args: argparse.Namespace) -> int:
    techniques, suite = _load_validated_suite(args)
    if techniques is None or suite is None:
        return 1
    cases = build_manual_cases(suite, techniques, limit=args.limit)
    markdown = render_manual_markdown(suite, cases)
    if args.output:
        output_path = Path(args.output)
    else:
        REPORTS_DIR.mkdir(exist_ok=True)
        output_path = REPORTS_DIR / f"{suite.id}-manual.md"
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Wrote {len(cases)} cases to {output_path}")
    return 0


def _write_execution_outputs(args: argparse.Namespace, suite, cases, target_name: str) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    markdown_path = (
        Path(args.output) if args.output else REPORTS_DIR / f"{suite.id}-{target_name}.md"
    )
    jsonl_path = markdown_path.with_suffix(".jsonl")
    markdown_path.write_text(
        render_execution_markdown(suite, cases, target_name),
        encoding="utf-8",
    )
    write_jsonl_report(jsonl_path, cases, suite, target_name)
    findings = sum(1 for case in cases if case.findings)
    print(f"Wrote {len(cases)} cases to {markdown_path}")
    print(f"Wrote machine-readable results to {jsonl_path}")
    print(f"Detector hits: {findings}")


def _run_mock_command(args: argparse.Namespace) -> int:
    techniques, suite = _load_validated_suite(args)
    if techniques is None or suite is None:
        return 1
    target = vulnerable_mock_target if args.profile == "vulnerable" else safe_mock_target
    cases = run_cases(suite, techniques, target, limit=args.limit)
    _write_execution_outputs(args, suite, cases, f"mock-{args.profile}")
    return 0


def _run_rest_command(args: argparse.Namespace) -> int:
    techniques, suite = _load_validated_suite(args)
    if techniques is None or suite is None:
        return 1

    def target(prompt: str) -> str:
        return post_json_target(
            args.url,
            prompt,
            prompt_field=args.prompt_field,
            response_field=args.response_field,
            timeout=args.timeout,
        )

    cases = run_cases(suite, techniques, target, limit=args.limit)
    _write_execution_outputs(args, suite, cases, "rest")
    return 0


def _mutate_command(args: argparse.Namespace) -> int:
    mutator = MUTATORS[args.mutator]
    print(mutator(args.text))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="redteam-llm")
    subparsers = parser.add_subparsers(dest="command", required=True)

    catalog = subparsers.add_parser("catalog")
    catalog_sub = catalog.add_subparsers(dest="catalog_action", required=True)
    catalog_sub.add_parser("validate")
    catalog_list = catalog_sub.add_parser("list")
    catalog_list.add_argument("--family")
    catalog_list.add_argument("--tag")

    suite = subparsers.add_parser("suite")
    suite_sub = suite.add_subparsers(dest="suite_action", required=True)
    suite_sub.add_parser("list")
    suite_show = suite_sub.add_parser("show")
    suite_show.add_argument("--suite", default="quick-smoke")

    run = subparsers.add_parser("run")
    run_sub = run.add_subparsers(dest="run_action", required=True)
    manual = run_sub.add_parser("manual")
    manual.add_argument("--suite", default="quick-smoke")
    manual.add_argument("--limit", type=int)
    manual.add_argument("--output")
    mock = run_sub.add_parser("mock")
    mock.add_argument("--suite", default="quick-smoke")
    mock.add_argument("--limit", type=int)
    mock.add_argument("--profile", choices=["safe", "vulnerable"], default="vulnerable")
    mock.add_argument("--output")
    rest = run_sub.add_parser("rest")
    rest.add_argument("--suite", default="quick-smoke")
    rest.add_argument("--limit", type=int)
    rest.add_argument("--url", required=True)
    rest.add_argument("--prompt-field", default="prompt")
    rest.add_argument("--response-field", default="response")
    rest.add_argument("--timeout", type=int, default=30)
    rest.add_argument("--output")

    mutate = subparsers.add_parser("mutate")
    mutate.add_argument("mutator", choices=sorted(MUTATORS))
    mutate.add_argument("text")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "catalog":
        return _catalog_command(args)
    if args.command == "suite":
        return _suite_command(args)
    if args.command == "run":
        if args.run_action == "manual":
            return _run_manual_command(args)
        if args.run_action == "mock":
            return _run_mock_command(args)
        if args.run_action == "rest":
            return _run_rest_command(args)
    if args.command == "mutate":
        return _mutate_command(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
