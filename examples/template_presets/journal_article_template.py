"""Standalone JournalArticleTemplate customization example."""

from __future__ import annotations

from pathlib import Path

from docscriptor import (
    AuthorLayout,
    BlockOptions,
    CaptionOptions,
    GeneratedPageOptions,
    PageMargins,
    PageNumberOptions,
    PageSize,
    Theme,
    TitleMatterOptions,
    TypographyOptions,
)
from docscriptor.presets.templates import JournalArticleTemplate

from common import sample_authors, sample_citations, sample_sections, save_template_document


def build_document():
    """Build a custom journal-like manuscript preset."""

    citations = sample_citations()
    template = JournalArticleTemplate(
        name="Lab report article",
        theme=Theme(
            TypographyOptions(body_font_name="Arial", body_font_size=10.5, title_font_size=17),
            CaptionOptions(caption_alignment="left", table_caption_position="above"),
            GeneratedPageOptions(generated_section_level=1, generated_page_breaks=False),
            PageNumberOptions(show_page_numbers=True, page_number_alignment="right"),
            TitleMatterOptions(title_alignment="left", subtitle_alignment="left", author_alignment="left"),
            BlockOptions(paragraph_alignment="justify", table_alignment="center", figure_alignment="center"),
        ),
        page_size=PageSize.letter(),
        page_margins=PageMargins.symmetric(vertical=1.0, horizontal=1.1, unit="in"),
        author_layout=AuthorLayout(mode="stacked", show_details=True),
        include_contents=True,
    )
    return template.build(
        "Template Preset Example: Custom JournalArticleTemplate",
        subtitle="A small institutional template built from the base preset",
        authors=sample_authors(),
        abstract="This example customizes JournalArticleTemplate with local typography, margins, title matter, and generated-page defaults.",
        keywords=["docscriptor", "custom template", "lab report"],
        sections=sample_sections(citations),
        citations=citations,
        summary="Custom JournalArticleTemplate preset example",
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
