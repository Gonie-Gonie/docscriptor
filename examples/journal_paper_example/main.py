"""Standalone journal paper example for docscriptor."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

from docscriptor import (
    Chapter,
    CitationLibrary,
    CitationSource,
    Document,
    Figure,
    Paragraph,
    ParagraphStyle,
    ReferencesPage,
    Section,
    Table,
    TableStyle,
    Text,
)

matplotlib.use("Agg")

import matplotlib.pyplot as plt


OUTPUT_DIR = Path("artifacts") / "journal-paper"
EXAMPLE_DIR = Path(__file__).resolve().parent
ASSET_DIR = EXAMPLE_DIR / "assets"
SYSTEM_DIAGRAM_PATH = ASSET_DIR / "system-diagram.png"
RESULTS_CSV_PATH = ASSET_DIR / "benchmark_results.csv"
ABLATION_CSV_PATH = ASSET_DIR / "ablation_results.csv"


def build_performance_figure(results_df: pd.DataFrame):
    """Create a matplotlib figure directly from the benchmark CSV data."""

    figure, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))

    axes[0].bar(results_df["Model"], results_df["Accuracy"], color="#4C78A8")
    axes[0].set_title("Accuracy")
    axes[0].set_ylabel("Score")
    axes[0].set_ylim(0.80, 1.00)
    axes[0].tick_params(axis="x", rotation=20)

    axes[1].plot(
        results_df["Model"],
        results_df["Latency_ms"],
        marker="o",
        linewidth=2,
        color="#F58518",
    )
    axes[1].set_title("Latency")
    axes[1].set_ylabel("ms")
    axes[1].tick_params(axis="x", rotation=20)

    figure.tight_layout()
    return figure


def build_journal_paper_document() -> Document:
    """Build an example journal-style manuscript."""

    results_df = pd.read_csv(RESULTS_CSV_PATH)
    ablation_df = pd.read_csv(ABLATION_CSV_PATH)

    manuscript_sources = CitationLibrary(
        [
            CitationSource(
                "Benchmark protocol for reproducible scientific reporting",
                key="benchmark-protocol",
                organization="Open Research Consortium",
                year="2025",
                url="https://example.org/benchmark-protocol",
            ),
            CitationSource(
                "Document automation workflows in applied research teams",
                key="automation-survey",
                authors=("A. Park", "J. Singh"),
                publisher="Practical Research Systems",
                year="2024",
                url="https://example.org/automation-survey",
            ),
        ]
    )

    benchmark_table = Table.from_dataframe(
        results_df[["Model", "Accuracy", "F1", "Latency_ms"]],
        caption="Benchmark results loaded directly from the experiment CSV file.",
        column_widths=[1.6, 1.2, 1.0, 1.3],
        style=TableStyle(
            header_background_color="#DCE8F4",
            alternate_row_background_color="#F7FAFD",
        ),
    )
    ablation_table = Table.from_dataframe(
        ablation_df,
        caption="Ablation results for major document-pipeline design decisions.",
        column_widths=[2.4, 1.2, 1.0],
        style=TableStyle(
            header_background_color="#E3ECF6",
            alternate_row_background_color="#F8FBFD",
        ),
    )
    system_diagram = Figure(
        SYSTEM_DIAGRAM_PATH,
        caption=Paragraph(
            "System overview diagram stored under the example asset directory."
        ),
        width_inches=5.2,
    )
    performance_figure = Figure(
        build_performance_figure(results_df),
        caption=Paragraph(
            "Accuracy and latency curves generated directly from the benchmark CSV with matplotlib."
        ),
        width_inches=6.0,
    )

    return Document(
        "A Python-Native Workflow for Reproducible Journal Manuscripts",
        Paragraph(
            "Jiyoon Kim, Minho Lee, and Sujin Park",
            style=ParagraphStyle(alignment="center", space_after=4),
        ),
        Paragraph(
            Text.italic("Department of Computational Publishing, Seoul"),
            style=ParagraphStyle(alignment="center", space_after=16),
        ),
        Chapter(
            "Abstract",
            Paragraph(
                "This example models a journal submission workflow where prose, tables, and figures are assembled from ordinary Python code. Benchmark tables are loaded from CSV files with ",
                Text.code("pandas.read_csv"),
                ", plots are created with ",
                Text.code("matplotlib"),
                ", and both DOCX and PDF outputs are rendered from the same source document. The workflow follows the reporting discipline described in ",
                manuscript_sources.cite("benchmark-protocol"),
                ".",
            ),
            Paragraph(
                Text.italic("Keywords: "),
                "scientific reporting, document automation, reproducible workflows, Python",
            ),
        ),
        Chapter(
            "Highlights",
            Paragraph("1. Tables can be authored directly from CSV-backed DataFrames."),
            Paragraph("2. Matplotlib figures can be inserted without saving temporary image files."),
            Paragraph("3. The same manuscript source renders to both DOCX and PDF for review and submission."),
        ),
        Chapter(
            "Introduction",
            Paragraph(
                "Research groups often maintain result tables in spreadsheets or CSV exports while figures are assembled separately for manuscript submission. This example keeps those assets connected by treating the document itself as Python code."
            ),
            Paragraph(
                "The broader motivation also aligns with practical automation patterns discussed in ",
                manuscript_sources.cite("automation-survey"),
                ".",
            ),
        ),
        Chapter(
            "Methods",
            Section(
                "Asset Layout",
                Paragraph(
                    "The example assumes an asset directory that already contains a system diagram PNG and experiment result CSV files. That layout mirrors a small research project more closely than generating all assets inline."
                ),
                system_diagram,
            ),
            Section(
                "Data Integration",
                Paragraph(
                    "The benchmark and ablation tables below are both loaded from CSV files into DataFrames before being passed directly into ",
                    Text.code("Table.from_dataframe(...)"),
                    ". The performance plot is produced from the same benchmark DataFrame and inserted as a live matplotlib figure object."
                ),
            ),
        ),
        Chapter(
            "Results",
            Section(
                "Benchmark Performance",
                Paragraph(
                    "As summarized in ",
                    benchmark_table,
                    ", the held-out evaluation set improves as more review automation is added. The same CSV data is visualized in ",
                    performance_figure,
                    ".",
                ),
                benchmark_table,
                performance_figure,
            ),
            Section(
                "Ablation Study",
                Paragraph(
                    "A smaller ablation CSV can be inserted without changing the document model. The same path from CSV to DataFrame to renderable table is reused for ",
                    ablation_table,
                    ".",
                ),
                ablation_table,
            ),
        ),
        Chapter(
            "Discussion",
            Paragraph(
                "For many applied teams, the primary value is not a new layout feature but the reduction in manual copying. When tables and figures are regenerated from the same inputs that produced the analysis, late revisions become safer and faster."
            ),
        ),
        Chapter(
            "Acknowledgements",
            Paragraph(
                "The authors thank the internal review group for feedback on manuscript structure and benchmark presentation."
            ),
        ),
        ReferencesPage(),
        author="Jiyoon Kim; Minho Lee; Sujin Park",
        summary="Journal-style example manuscript",
        citations=manuscript_sources,
    )


def build_journal_paper(output_dir: str | Path) -> tuple[Path, Path]:
    """Build the journal paper example and export it to DOCX and PDF."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    document = build_journal_paper_document()
    docx_path = output_path / "journal-paper.docx"
    pdf_path = output_path / "journal-paper.pdf"
    document.save_docx(docx_path)
    document.save_pdf(pdf_path)
    return docx_path, pdf_path


def main() -> None:
    """Build the paper into the default example output directory."""

    docx_path, pdf_path = build_journal_paper(OUTPUT_DIR)
    print(f"Wrote {docx_path}")
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    main()
