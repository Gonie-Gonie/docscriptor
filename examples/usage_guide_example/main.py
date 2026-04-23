"""Standalone usage guide example for docscriptor."""

from __future__ import annotations

from pathlib import Path

from docscriptor import (
    BulletList,
    Chapter,
    CitationLibrary,
    CitationSource,
    Comment,
    CommentsPage,
    CodeBlock,
    Document,
    Equation,
    Figure,
    FigureList,
    Footnote,
    FootnotesPage,
    ListStyle,
    Math,
    NumberedList,
    Paragraph,
    ParagraphStyle,
    ReferencesPage,
    Section,
    Table,
    TableList,
    TableOfContents,
    Text,
    Theme,
)


OUTPUT_DIR = Path("artifacts") / "usage-guide"
EXAMPLE_DIR = Path(__file__).resolve().parent
ASSET_DIR = EXAMPLE_DIR / "assets"
FIGURE_PATH = ASSET_DIR / "usage-guide-figure.png"

RELATED_WORK_BIBTEX = """@article{knuth1984literate,
  author = {Donald E. Knuth},
  title = {Literate Programming},
  journal = {The Computer Journal},
  volume = {27},
  number = {2},
  pages = {97--111},
  year = {1984},
  publisher = {Oxford University Press},
  url = {https://doi.org/10.1093/comjnl/27.2.97}
}"""

QUICK_START_SNIPPET = """from docscriptor import Chapter, Document, Paragraph, Section

report = Document(
    "Hello docscriptor",
    Chapter(
        "Getting Started",
        Section(
            "Overview",
            Paragraph("This document was defined with Python objects."),
        ),
    ),
)

report.save_docx("artifacts/hello.docx")
report.save_pdf("artifacts/hello.pdf")
"""

REUSABLE_SNIPPET = """from docscriptor import Paragraph, ParagraphStyle, Text


class WarningParagraph(Paragraph):
    def __init__(self, *content):
        super().__init__(
            Text.bold("Warning: "),
            *content,
            style=ParagraphStyle(space_after=14),
        )
"""


def build_usage_guide_document() -> Document:
    """Build the in-memory usage guide document."""

    related_work = CitationLibrary.from_bibtex(RELATED_WORK_BIBTEX)
    repository_source = CitationSource(
        "pydocs",
        organization="Gonie-Gonie",
        publisher="GitHub repository",
        year="2026",
        url="https://github.com/Gonie-Gonie/pydocs",
    )

    core_blocks_table = Table(
        headers=["Kind", "Examples", "Purpose"],
        rows=[
            [
                "Structure",
                "Document, Chapter, Section, Paragraph",
                "Build a readable document tree directly with Python objects.",
            ],
            [
                "Content",
                "BulletList, NumberedList, CodeBlock, Table, Figure",
                "Mix prose, lists, code, tables, and images in one source file.",
            ],
            [
                "Inline actions",
                "Text.bold, Text.from_markup, Comment.annotated",
                "Apply styling or annotations where content is authored.",
            ],
        ],
        caption="Core authoring primitives.",
        column_widths=[1.5, 3.1, 2.0],
    )
    output_table = Table(
        headers=["Goal", "Preferred Output"],
        rows=[
            ["Editable review", "DOCX"],
            ["Stable distribution", "PDF"],
        ],
        caption="Rendering outputs by goal.",
        column_widths=[2.5, 2.2],
    )
    preview_figure = Figure(
        FIGURE_PATH,
        caption=Paragraph(
            "Example figure loaded directly from the example asset directory."
        ),
        width_inches=1.7,
    )

    return Document(
        "Using docscriptor",
        TableList(),
        FigureList(),
        TableOfContents(),
        Chapter(
            "Getting Started",
            Section(
                "Quick Start",
                Paragraph(
                    "Build a document tree with Python objects and render the same structure to ",
                    Text.styled("DOCX", bold=True),
                    " and ",
                    Text.styled("PDF", bold=True),
                    ".",
                    style=ParagraphStyle(space_after=14),
                ),
                Paragraph(
                    "Use classes such as ",
                    Text.bold("Document"),
                    ", ",
                    Text.bold("Chapter"),
                    ", ",
                    Text.bold("Section"),
                    ", and ",
                    Text.bold("Paragraph"),
                    " for structure. Inline actions stay explicit with methods such as ",
                    Text.code("Text.bold(...)"),
                    " and ",
                    Text.code("Text.from_markup(...)"),
                    ".",
                ),
                output_table,
                NumberedList(
                    "Import the objects you need.",
                    "Compose sections and paragraphs as regular Python instances.",
                    "Call save_docx() and save_pdf() on the document.",
                ),
                CodeBlock(QUICK_START_SNIPPET, language="python"),
            ),
        ),
        Chapter(
            "Authoring Model",
            Section(
                "Core Blocks",
                Paragraph(
                    "Tables and figures can be referenced directly by reusing the same object instance. See ",
                    core_blocks_table,
                    " for the main building blocks and ",
                    preview_figure,
                    " for a simple asset-based figure example.",
                ),
                core_blocks_table,
                preview_figure,
                BulletList(
                    "Keep reusable assets in an asset directory beside the example script.",
                    "Use Tables for structured summaries that should stay synchronized across outputs.",
                    "Use Figures for either stored files or savefig()-compatible Python objects.",
                ),
            ),
            Section(
                "Inline Actions",
                Paragraph(
                    "Text styling can stay explicit with ",
                    Text.code("Text.bold"),
                    " and ",
                    Text.code("Text.styled"),
                    ", while markdown-like content can still be written with ",
                    Text.code("Text.from_markup"),
                    ".",
                ),
                Paragraph(
                    "This sentence mixes ",
                    Text.from_markup("**bold** text, *italic* text, and `code` fragments"),
                    " inside one paragraph.",
                ),
                Paragraph(
                    "Portable comments such as ",
                    Comment.annotated(
                        "review note",
                        "Comments are collected on a generated comments page.",
                    ),
                    ", footnotes such as ",
                    Footnote.annotated(
                        "term",
                        "Portable footnotes remain stable in both DOCX and PDF.",
                    ),
                    ", and inline math such as ",
                    Math.inline(r"\alpha^2 + \beta^2 = \gamma^2"),
                    " can all be authored in plain Python.",
                ),
                Equation(r"\int_0^1 \alpha x^2 \, dx = \frac{\alpha}{3}"),
                Paragraph(
                    "The project repository can be cited directly as ",
                    repository_source.cite(),
                    ", and related work can be cited from a small library as ",
                    related_work.cite("knuth1984literate"),
                    ".",
                ),
            ),
            Section(
                "Reusable Patterns",
                Paragraph(
                    "When a pattern repeats, subclassing a block is often enough. The example below keeps the custom logic small and local."
                ),
                CodeBlock(REUSABLE_SNIPPET, language="python"),
            ),
        ),
        FootnotesPage(),
        CommentsPage(),
        ReferencesPage(),
        author="docscriptor examples",
        summary="Usage guide document",
        theme=Theme(
            show_page_numbers=True,
            page_number_format="Page {page}",
            bullet_list_style=ListStyle(
                marker_format="bullet",
                bullet="\u2022",
                suffix="",
            ),
        ),
        citations=related_work,
    )


def build_usage_guide(output_dir: str | Path) -> tuple[Path, Path]:
    """Build the usage guide and export it to DOCX and PDF."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    document = build_usage_guide_document()
    docx_path = output_path / "docscriptor-usage-guide.docx"
    pdf_path = output_path / "docscriptor-usage-guide.pdf"
    document.save_docx(docx_path)
    document.save_pdf(pdf_path)
    return docx_path, pdf_path


def main() -> None:
    """Build the guide into the default example output directory."""

    docx_path, pdf_path = build_usage_guide(OUTPUT_DIR)
    print(f"Wrote {docx_path}")
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    main()
