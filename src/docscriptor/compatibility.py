"""Shared output-format compatibility helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal


OutputFormat = Literal["docx", "pdf", "html"]
OUTPUT_FORMATS: tuple[OutputFormat, ...] = ("docx", "pdf", "html")
OUTPUT_FORMAT_LABELS: dict[OutputFormat, str] = {
    "docx": "Word",
    "pdf": "PDF",
    "html": "HTML",
}


@dataclass(frozen=True, slots=True)
class CompatibilityNote:
    """Renderer compatibility note surfaced by document validation."""

    code: str
    message: str
    formats: tuple[OutputFormat, ...]


COMPATIBILITY_NOTES: dict[str, CompatibilityNote] = {
    "html-toc-page-numbers": CompatibilityNote(
        code="html-toc-page-numbers",
        message=(
            "HTML output does not have stable rendered page numbers, "
            "so the TOC is link-only there."
        ),
        formats=("html",),
    ),
}


def compatibility_note(code: str) -> CompatibilityNote:
    """Return a named compatibility note."""

    try:
        return COMPATIBILITY_NOTES[code]
    except KeyError as exc:
        raise KeyError(f"Unknown compatibility note: {code}") from exc


def normalize_output_format(value: str) -> OutputFormat:
    """Normalize a renderer/output format name."""

    normalized = value.lower().strip().removeprefix(".")
    if normalized == "htm":
        normalized = "html"
    if normalized not in OUTPUT_FORMATS:
        raise ValueError(
            "Unsupported document output format. Use one of: .docx, .pdf, .html "
            "(or docx, pdf, html in save_all)."
        )
    return normalized  # type: ignore[return-value]


def normalize_output_formats(
    values: Iterable[str] | None = None,
) -> tuple[OutputFormat, ...]:
    """Normalize a sequence of output formats while preserving order."""

    if values is None:
        return OUTPUT_FORMATS

    normalized: list[OutputFormat] = []
    seen: set[OutputFormat] = set()
    for value in values:
        output_format = normalize_output_format(value)
        if output_format in seen:
            continue
        normalized.append(output_format)
        seen.add(output_format)
    return tuple(normalized)


def format_output_formats(formats: Iterable[OutputFormat]) -> str:
    """Return a compact display label for output formats."""

    normalized = normalize_output_formats(formats)
    if not normalized:
        return "None"
    if set(normalized) == set(OUTPUT_FORMATS):
        return "All"
    return "/".join(OUTPUT_FORMAT_LABELS[output_format] for output_format in normalized)


__all__ = [
    "COMPATIBILITY_NOTES",
    "OUTPUT_FORMATS",
    "OUTPUT_FORMAT_LABELS",
    "CompatibilityNote",
    "OutputFormat",
    "compatibility_note",
    "format_output_formats",
    "normalize_output_format",
    "normalize_output_formats",
]
