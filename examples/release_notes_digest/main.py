"""Build a release-note digest from the repository Markdown files."""

from __future__ import annotations

from pathlib import Path
import re

from docscriptor import (
    Chapter,
    Document,
    DocumentSettings,
    Figure,
    NumberedList,
    Paragraph,
    Section,
    Table,
    TableOfContents,
    Theme,
    code,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_DIR = Path(__file__).resolve().parent
ASSET_DIR = EXAMPLE_DIR / "assets"
RELEASE_NOTES_DIR = REPO_ROOT / "release-notes"
OUTPUT_DIR = Path("artifacts") / "release-notes"
RELEASE_DIGEST_DIAGRAM_PATH = ASSET_DIR / "release-digest-workflow.png"
VERSION_FILENAME_RE = re.compile(
    r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)\.md$"
)


def version_parts_from_filename(path: Path) -> tuple[int, int, int]:
    """Read a semantic version tuple from a file such as ``v0.9.1.md``."""

    match = VERSION_FILENAME_RE.fullmatch(path.name)
    if match is None:
        raise ValueError(
            f"Release note filename must match vMAJOR.MINOR.PATCH.md: {path.name}"
        )
    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
    )


def release_note_files(release_notes_dir: str | Path = RELEASE_NOTES_DIR) -> list[Path]:
    """Return release-note Markdown files sorted from newest to oldest."""

    notes_dir = Path(release_notes_dir)
    files = sorted(
        notes_dir.glob("*.md"),
        key=version_parts_from_filename,
        reverse=True,
    )
    if not files:
        raise FileNotFoundError(f"No release note Markdown files found in {notes_dir}")
    return files


def release_type_from_version(version_parts: tuple[int, int, int]) -> str:
    """Classify a semantic version as Major, Minor, or Patch."""

    if version_parts[2] > 0:
        return "Patch"
    if version_parts[1] > 0:
        return "Minor"
    return "Major"


def repo_relative(path: Path) -> str:
    """Show repository paths in a compact form inside the generated document."""

    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def section_titles(markdown_text: str) -> str:
    """List the second-level headings in one release-note Markdown file."""

    titles: list[str] = []
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            titles.append(stripped.removeprefix("## ").strip())
    return ", ".join(titles) or "Release notes"


def build_release_notes_document(
    release_notes_dir: str | Path = RELEASE_NOTES_DIR,
) -> Document:
    """Build the release-note digest document from Markdown files."""

    files = release_note_files(release_notes_dir)
    release_index_rows = []
    release_sections = []

    for index, path in enumerate(files):
        version = path.stem
        version_parts = version_parts_from_filename(path)
        release_type = release_type_from_version(version_parts)
        markdown_text = path.read_text(encoding="utf-8")
        imported_release = Document.from_markdown(
            markdown_text,
            numbered=False,
            toc=False,
            heading_level_shift=1,
        )

        release_index_rows.append(
            [
                f"{version} (latest)" if index == 0 else version,
                release_type,
                path.name,
                section_titles(markdown_text),
            ]
        )

        release_sections.append(
            Section(
                version,
                Paragraph(
                    "Imported from ",
                    code(repo_relative(path)),
                    " after semantic-version sorting.",
                ),
                imported_release.body.children,
                level=2,
                numbered=False,
                toc=True,
            )
        )

    latest_release = files[0]
    latest_version = latest_release.stem
    digest_workflow_figure = Figure(
        RELEASE_DIGEST_DIAGRAM_PATH,
        caption=Paragraph(
            "Release-note digest workflow from versioned Markdown files to the rendered output bundle."
        ),
        width=6.5,
    )
    release_index_table = Table(
        headers=["Version", "Type", "File", "Sections"],
        rows=release_index_rows,
        caption="Release note files collected from the repository.",
        column_widths=[2.6, 1.6, 2.8, 9.0],
        unit="cm",
        header_background_color="#E7EEF7",
        alternate_row_background_color="#F8FBFD",
    )
    version_management_table = Table(
        headers=["Concern", "Repository practice"],
        rows=[
            [
                "Version source",
                "Package versions are derived from git tags through setuptools-scm.",
            ],
            [
                "Tag format",
                "Use vMAJOR.MINOR.PATCH, matching the release note filename.",
            ],
            [
                "Current release",
                f"{latest_version} from {repo_relative(latest_release)}.",
            ],
            [
                "Release body",
                "The GitHub release workflow uses release-notes/<tag>.md when it exists.",
            ],
            [
                "Output bundle",
                "The same digest can be exported as DOCX, PDF, and HTML for review.",
            ],
        ],
        caption="Version-management rules demonstrated by this example.",
        column_widths=[3.0, 12.0],
        unit="cm",
        header_background_color="#E8F2EC",
        alternate_row_background_color="#FAFCFA",
    )

    return Document(
        "Docscriptor Release Notes",
        TableOfContents(max_level=2),
        Chapter(
            "Release Note Index",
            Paragraph(
                "This example gathers Markdown files from ",
                code(repo_relative(Path(release_notes_dir))),
                ", reads version metadata from filenames such as ",
                code("v0.9.1.md"),
                ", and sorts the imported notes from newest to oldest.",
            ),
            digest_workflow_figure,
            release_index_table,
        ),
        Chapter(
            "Version Management",
            Paragraph(
                "The repository keeps release intent close to the code: the tag controls "
                "the package version, and the matching Markdown file controls the curated "
                "release body."
            ),
            version_management_table,
            Section(
                "Release runbook",
                NumberedList(
                    Paragraph("Write or update ", code("release-notes/vX.Y.Z.md"), "."),
                    Paragraph(
                        "Check the version follows ",
                        code("vMAJOR.MINOR.PATCH"),
                        " and describe compatibility notes explicitly.",
                    ),
                    Paragraph(
                        "Run ",
                        code(".\\scripts\\release.ps1 X.Y.Z"),
                        " to create and push the matching tag.",
                    ),
                    Paragraph(
                        "Let the release workflow test, build, render examples, publish the "
                        "GitHub Release, and upload distributions to PyPI.",
                    ),
                ),
            ),
        ),
        Chapter(
            "Version History",
            Paragraph(
                "Each version below is imported from the matching Markdown file. "
                "The version headings stay visible in the contents, while release-note "
                "subsections such as Highlights and Compatibility Notes stay local to "
                "each version body."
            ),
            release_sections,
        ),
        settings=DocumentSettings(
            metadata_author="Docscriptor Contributors",
            summary="Release-note digest generated from repository Markdown files",
            subtitle="Markdown import, semantic sorting, and release workflow documentation",
            theme=Theme(show_page_numbers=True, page_number_format="{page}"),
        ),
    )


def build_release_notes(
    output_dir: str | Path,
    *,
    verbose: bool = False,
) -> tuple[Path, Path]:
    """Build the release-note digest and export it to DOCX, PDF, and HTML."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    document = build_release_notes_document()
    outputs = document.save_all(
        output_path,
        stem="docscriptor-release-notes",
        verbose=verbose,
    )
    return outputs["docx"], outputs["pdf"]


def main() -> None:
    """Build the release-note digest into the default example output directory."""

    docx_path, pdf_path = build_release_notes(OUTPUT_DIR, verbose=True)
    html_path = OUTPUT_DIR / "docscriptor-release-notes.html"
    print(f"Wrote {docx_path}")
    print(f"Wrote {pdf_path}")
    print(f"Wrote {html_path}")


if __name__ == "__main__":
    main()
