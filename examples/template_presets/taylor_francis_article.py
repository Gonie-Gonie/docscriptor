"""Standalone TaylorFrancisArticle template preset example."""

from __future__ import annotations

from pathlib import Path

from docscriptor.presets.templates import TaylorFrancisArticle

from common import sample_authors, sample_citations, sample_sections, save_template_document


def build_document():
    """Build a Taylor & Francis-like manuscript draft."""

    citations = sample_citations()
    template = TaylorFrancisArticle(include_contents=True)
    return template.build(
        "Template Preset Example: Taylor & Francis Article",
        subtitle="Left-aligned title matter with manuscript-style defaults",
        authors=sample_authors(),
        abstract="This example shows the TaylorFrancisArticle preset using the same manuscript input shape with a different house layout.",
        keywords=["docscriptor", "Taylor & Francis", "template preset"],
        sections=sample_sections(citations),
        citations=citations,
        summary="TaylorFrancisArticle preset example",
    )


def build(output_dir: str | Path = Path("artifacts") / "template") -> dict[str, Path]:
    """Render the example into the template artifact directory."""

    return save_template_document(build_document(), "taylor-francis-article", output_dir)


def main() -> None:
    """Build the example from the command line."""

    for path in build().values():
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
