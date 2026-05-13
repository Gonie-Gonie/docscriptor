"""Standalone content-first JournalArticleTemplate example."""

from __future__ import annotations

from pathlib import Path

from docscriptor.presets.templates import JournalArticleTemplate

from common import (
    sample_acknowledgements,
    sample_abstract,
    sample_authors,
    sample_citations,
    sample_data_availability,
    sample_keywords,
    sample_sections,
    save_template_document,
)


def build_document():
    """Build a journal manuscript from content-oriented inputs."""

    citations = sample_citations()
    return JournalArticleTemplate().build(
        "Content-First Journal Article Template",
        subtitle="A ready manuscript draft from article metadata and body sections",
        authors=sample_authors(),
        abstract=sample_abstract(),
        keywords=sample_keywords(),
        sections=sample_sections(citations),
        acknowledgements=sample_acknowledgements(),
        data_availability=sample_data_availability(),
        citations=citations,
        summary="Content-first JournalArticleTemplate preset example",
    )


def build(output_dir: str | Path = Path("artifacts") / "template") -> dict[str, Path]:
    """Render the example into the template artifact directory."""

    return save_template_document(build_document(), "journal-article-template", output_dir)


def main() -> None:
    """Build the example from the command line."""

    for path in build().values():
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
