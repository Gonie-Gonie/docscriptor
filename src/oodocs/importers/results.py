"""Shared import diagnostics for Markdown and notebook importers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Sequence

from oodocs.components.base import Block
from oodocs.core import OODocsError


ImportSeverity = Literal["info", "warning", "error"]
ImportPolicy = Literal["lossy", "warn", "strict"]


@dataclass(frozen=True, slots=True)
class ImportIssue:
    """One issue reported while importing a lossy external source."""

    severity: ImportSeverity
    code: str
    message: str
    line: int | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "source": self.source,
        }


@dataclass(frozen=True, slots=True)
class ImportResult:
    """Imported blocks plus optional diagnostics."""

    blocks: tuple[Block, ...]
    issues: tuple[ImportIssue, ...] = ()

    def warnings(self) -> tuple[ImportIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "warning")

    def errors(self) -> tuple[ImportIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "error")

    def format_issues(self) -> str:
        if not self.issues:
            return "OODocs import completed with 0 issue(s)."
        lines = [f"OODocs import completed with {len(self.issues)} issue(s):"]
        for issue in self.issues:
            location = f" line {issue.line}" if issue.line is not None else ""
            source = f" in {issue.source}" if issue.source else ""
            lines.append(
                f"- {issue.severity.upper()} {issue.code}{source}{location}: "
                f"{issue.message}"
            )
        return "\n".join(lines)


class ImportPolicyError(OODocsError):
    """Raised when strict import policy rejects a lossy conversion."""

    def __init__(self, issues: Sequence[ImportIssue]) -> None:
        self.issues = tuple(issues)
        super().__init__(ImportResult((), self.issues).format_issues())


def normalize_import_policy(value: str) -> ImportPolicy:
    normalized = value.strip().lower()
    if normalized not in {"lossy", "warn", "strict"}:
        raise ValueError("import_policy must be 'lossy', 'warn', or 'strict'")
    return normalized  # type: ignore[return-value]


def resolve_import_result(
    blocks: Iterable[Block],
    issues: Iterable[ImportIssue],
    *,
    diagnostics: bool,
    import_policy: str,
) -> list[Block] | ImportResult:
    normalized_policy = normalize_import_policy(import_policy)
    normalized_blocks = tuple(blocks)
    normalized_issues = tuple(issues)
    if normalized_policy == "strict" and normalized_issues:
        raise ImportPolicyError(normalized_issues)
    if diagnostics:
        return ImportResult(normalized_blocks, normalized_issues)
    return list(normalized_blocks)


__all__ = [
    "ImportIssue",
    "ImportPolicy",
    "ImportPolicyError",
    "ImportResult",
    "ImportSeverity",
    "normalize_import_policy",
    "resolve_import_result",
]
