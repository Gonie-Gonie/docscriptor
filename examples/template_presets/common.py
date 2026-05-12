"""Shared article content for template preset examples."""

from __future__ import annotations

from pathlib import Path

from docscriptor import (
    Affiliation,
    Author,
    CitationLibrary,
    CitationSource,
    Paragraph,
    Table,
    code,
)
from docscriptor.presets.components import CalloutBox
from docscriptor.presets.templates import ManuscriptSection


OUTPUT_DIR = Path("artifacts") / "template"


def sample_authors() -> list[Author]:
    """Return structured author metadata shared by template examples."""

    return [
        Author(
            "Hyeong-Gon Jo",
            affiliations=[
                Affiliation(
                    department="Building Simulation LAB",
                    organization="Seoul National University",
                    city="Seoul",
                    country="Republic of Korea",
                )
            ],
            email="goniegonie@example.com",
            corresponding=True,
        ),
        Author(
            "Docscriptor Contributors",
            affiliations=["Open-source document tooling"],
        ),
    ]


def sample_citations() -> CitationLibrary:
    """Return a tiny citation library used by the manuscript body."""

    return CitationLibrary(
        [
            CitationSource(
                "Literate Programming",
                key="literate-programming",
                authors=("Donald E. Knuth",),
                publisher="The Computer Journal",
                year="1984",
                url="https://doi.org/10.1093/comjnl/27.2.97",
            ),
            CitationSource(
                "Statistical Analyses and Reproducible Research",
                key="reproducible-research",
                authors=("Robert Gentleman", "Duncan Temple Lang"),
                publisher="Journal of Computational and Graphical Statistics",
                year="2007",
                url="https://doi.org/10.1198/106186007X178663",
            ),
        ]
    )


def sample_sections(citations: CitationLibrary) -> list[ManuscriptSection]:
    """Return a compact manuscript body accepted by article templates."""

    feature_table = Table(
        headers=["Concern", "Template support"],
        rows=[
            ["Title matter", "Structured authors, affiliations, subtitle, and summary"],
            ["Body sections", "ManuscriptSection descriptors or ordinary Section blocks"],
            ["References", "CitationLibrary input plus an optional ReferencesPage"],
        ],
        caption="Template presets keep common manuscript pieces close to the input data.",
        header_background_color="#E7EEF7",
        alternate_row_background_color="#FAFCFE",
        cell_padding=4,
        repeat_header_rows=True,
    )
    note = CalloutBox(
        Paragraph(
            "Most local visual tweaks use direct kwargs. Style objects remain available when a lab or journal needs a reusable named style."
        ),
        title="Authoring preference",
        variant="note",
        padding=7,
    )
    return [
        ManuscriptSection(
            "Introduction",
            [
                Paragraph(
                    "Template presets are useful when the same manuscript-shaped document is rendered repeatedly. The content can stay in ordinary Python blocks while the preset owns page geometry, title matter, and generated reference defaults."
                ),
                Paragraph(
                    "The philosophy follows the traceability argument behind literate programming ",
                    citations.cite("literate-programming"),
                    " and reproducible research ",
                    citations.cite("reproducible-research"),
                    ".",
                ),
            ],
        ),
        ManuscriptSection(
            "Template Surface",
            [
                Paragraph(
                    "The body can be described with ",
                    code("ManuscriptSection"),
                    " objects, existing ",
                    code("Section"),
                    " blocks, or compact ",
                    code("(title, children)"),
                    " tuples.",
                ),
                feature_table,
                note,
            ],
        ),
        ManuscriptSection(
            "Conclusion",
            [
                Paragraph(
                    "Each template example in this directory is a complete script, so users can start from the closest file and still render every output format with ",
                    code("document.save_all(...)"),
                    ".",
                )
            ],
        ),
    ]


def save_template_document(document: object, stem: str, output_dir: str | Path = OUTPUT_DIR) -> dict[str, Path]:
    """Render a template example to DOCX, PDF, and HTML."""

    return document.save_all(output_dir, stem=stem)  # type: ignore[attr-defined]
