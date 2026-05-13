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
            CitationSource(
                "knitr: A General-Purpose Package for Dynamic Report Generation in R",
                key="knitr",
                authors=("Yihui Xie",),
                publisher="Official project site",
                year="2026",
                url="https://yihui.org/knitr/",
            ),
        ]
    )


def sample_abstract() -> str:
    """Return abstract text for the content-first journal template example."""

    return (
        "This example demonstrates a journal article template that owns common manuscript "
        "formatting while the author supplies only title matter, abstract text, keywords, "
        "body sections, optional declarations, and citation data. The resulting document "
        "uses conventional article ordering without requiring the caller to assemble a "
        "table of contents, generated table lists, figure lists, page geometry, or title "
        "matter layout by hand."
    )


def sample_keywords() -> list[str]:
    """Return keyword metadata for the template example."""

    return [
        "journal article",
        "document automation",
        "reproducible authoring",
        "python",
    ]


def sample_acknowledgements() -> str:
    """Return an optional acknowledgement statement for the template example."""

    return (
        "The authors thank the docscriptor maintainers and early readers for feedback on "
        "the manuscript preset API."
    )


def sample_data_availability() -> str:
    """Return an optional data availability statement for the template example."""

    return (
        "All inputs needed to regenerate this example are contained in the template preset "
        "example scripts and the citation metadata defined alongside them."
    )


def sample_sections(citations: CitationLibrary) -> list[ManuscriptSection]:
    """Return a compact manuscript body accepted by article templates."""

    study_table = Table(
        headers=["Input", "Author responsibility", "Template responsibility"],
        rows=[
            ["Title matter", "Provide title, authors, abstract, and keywords.", "Render journal-style title matter and front content."],
            ["Body", "Write detailed manuscript sections with tables, figures, and citations.", "Preserve numbered section hierarchy and references."],
            ["Declarations", "Provide optional statements only when needed.", "Omit empty acknowledgement and data availability sections."],
            ["References", "Provide citation metadata or disable references explicitly.", "Render a generated references section by default."],
        ],
        caption="Content-first journal templates separate manuscript content from repeated document assembly.",
        header_background_color="#E7EEF7",
        alternate_row_background_color="#FAFCFE",
        cell_padding=4,
        repeat_header_rows=True,
    )
    return [
        ManuscriptSection(
            "Introduction",
            [
                Paragraph(
                    "Journal manuscripts are repetitive in structure even when their arguments are unique. A useful template should therefore ask for manuscript facts, not for renderer details: title, authors, abstract, keywords, body sections, optional declarations, and references."
                ),
                Paragraph(
                    "The preset follows the traceability motivation behind literate programming ",
                    citations.cite("literate-programming"),
                    " and reproducible research ",
                    citations.cite("reproducible-research"),
                    ": the visible manuscript should remain downstream of structured inputs rather than hand-assembled formatting steps.",
                ),
            ],
        ),
        ManuscriptSection(
            "Methods",
            [
                Paragraph(
                    "The example builds the article with ",
                    code("JournalArticleTemplate.build(...)"),
                    ". The caller supplies the content surface directly and lets the template decide ordinary journal defaults such as title matter placement, page numbering, caption alignment, declaration ordering, and reference placement.",
                ),
                study_table,
            ],
        ),
        ManuscriptSection(
            "Results",
            [
                Paragraph(
                    "The body remains explicit because manuscript arguments are domain-specific. Authors can pass ",
                    code("ManuscriptSection"),
                    " descriptors, existing ",
                    code("Section"),
                    " blocks, or compact ",
                    code("(title, children)"),
                    " tuples, while the preset handles generated article structure around those blocks.",
                ),
                Paragraph(
                    "Optional acknowledgement and data availability statements behave like normal manuscript declarations: pass content to include the section, or pass ",
                    code("None"),
                    " to omit it without leaving an empty heading.",
                ),
            ],
        ),
        ManuscriptSection(
            "Discussion",
            [
                Paragraph(
                    "The template is intentionally generic rather than publisher-specific. It gives authors a complete article-shaped starting point, while still allowing project-specific overrides when a target journal has stricter instructions."
                ),
                Paragraph(
                    "This is similar in spirit to tools such as ",
                    citations.cite("knitr"),
                    ": the authoring environment should make repeatable structure cheap without hiding the scientific content that needs review.",
                ),
            ],
        ),
        ManuscriptSection(
            "Conclusion",
            [
                Paragraph(
                    "A content-first template lets authors fill in the manuscript fields that matter and receive a ready-to-render article draft without assembling theme, contents pages, generated lists, or declaration boilerplate by hand."
                ),
            ],
        ),
    ]


def save_template_document(document: object, stem: str, output_dir: str | Path = OUTPUT_DIR) -> dict[str, Path]:
    """Render a template example to DOCX, PDF, and HTML."""

    return document.save_all(output_dir, stem=stem)  # type: ignore[attr-defined]
