"""Standalone ElsevierArticle template preset example."""

from __future__ import annotations

from pathlib import Path

from docscriptor.presets.templates import ElsevierArticle

from common import sample_authors, sample_citations, sample_sections, save_template_document


def build_document():
    """Build an Elsevier-like manuscript draft."""

    citations = sample_citations()
    template = ElsevierArticle(include_contents=True)
    return template.build(
        "Template Preset Example: Elsevier Article",
        subtitle="Centered title matter with compact manuscript defaults",
        authors=sample_authors(),
        abstract="This example shows the ElsevierArticle preset building a complete document from title matter, sections, and citations.",
        keywords=["docscriptor", "templates", "manuscript automation"],
        sections=sample_sections(citations),
        citations=citations,
        summary="ElsevierArticle preset example",
    )


def build(output_dir: str | Path = Path("artifacts") / "template") -> dict[str, Path]:
    """Render the example into the template artifact directory."""

    return save_template_document(build_document(), "elsevier-article", output_dir)


def main() -> None:
    """Build the example from the command line."""

    for path in build().values():
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
