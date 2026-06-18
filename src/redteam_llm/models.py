from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SEVERITIES = {"P0", "P1", "P2", "P3"}


@dataclass(frozen=True)
class Technique:
    id: str
    title: str
    slug: str
    family: str
    tags: list[str]
    severity_hint: str
    source: str
    concept: str
    how_to: str
    examples: list[str]
    expected_safe_behavior: list[str]
    failure_signals: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Technique":
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            slug=str(data["slug"]),
            family=str(data["family"]),
            tags=list(data.get("tags", [])),
            severity_hint=str(data.get("severity_hint", "P1")),
            source=str(data.get("source", "")),
            concept=str(data.get("concept", "")),
            how_to=str(data.get("how_to", "")),
            examples=list(data.get("examples", [])),
            expected_safe_behavior=list(data.get("expected_safe_behavior", [])),
            failure_signals=list(data.get("failure_signals", [])),
        )


@dataclass(frozen=True)
class Suite:
    id: str
    title: str
    description: str
    technique_ids: list[str]
    recommended_mode: str = "manual-first"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Suite":
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            description=str(data.get("description", "")),
            technique_ids=list(data.get("technique_ids", [])),
            recommended_mode=str(data.get("recommended_mode", "manual-first")),
        )


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors
