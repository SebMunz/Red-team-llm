from __future__ import annotations

import json
from pathlib import Path

from .models import SEVERITIES, Suite, Technique, ValidationResult
from .paths import CATALOG_PATH, SUITES_DIR


def load_catalog(path: Path = CATALOG_PATH) -> list[Technique]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return [Technique.from_dict(item) for item in data.get("techniques", [])]


def load_suite(suite_id: str, suites_dir: Path = SUITES_DIR) -> Suite:
    path = suites_dir / f"{suite_id}.json"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return Suite.from_dict(data)


def list_suites(suites_dir: Path = SUITES_DIR) -> list[Suite]:
    suites: list[Suite] = []
    for path in sorted(suites_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        suites.append(Suite.from_dict(data))
    return suites


def validate_catalog(techniques: list[Technique]) -> ValidationResult:
    result = ValidationResult()
    seen_ids: set[str] = set()
    seen_slugs: set[str] = set()

    for technique in techniques:
        if technique.id in seen_ids:
            result.errors.append(f"Duplicate technique id: {technique.id}")
        seen_ids.add(technique.id)

        if technique.slug in seen_slugs:
            result.errors.append(f"Duplicate technique slug: {technique.slug}")
        seen_slugs.add(technique.slug)

        if technique.severity_hint not in SEVERITIES:
            result.errors.append(
                f"{technique.id} has invalid severity_hint {technique.severity_hint}"
            )
        if not technique.examples:
            result.warnings.append(f"{technique.id} has no examples")
        if not technique.concept:
            result.warnings.append(f"{technique.id} has no concept")
        if not technique.how_to:
            result.warnings.append(f"{technique.id} has no how_to")

    return result


def validate_suite(suite: Suite, techniques: list[Technique]) -> ValidationResult:
    result = ValidationResult()
    known_ids = {technique.id for technique in techniques}
    for technique_id in suite.technique_ids:
        if technique_id not in known_ids:
            result.errors.append(f"{suite.id} references unknown technique {technique_id}")
    return result
