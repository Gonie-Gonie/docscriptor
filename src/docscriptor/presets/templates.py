"""Document template presets for common manuscript-shaped documents."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from docscriptor.components.base import BlockInput
from docscriptor.components.blocks import Chapter, Paragraph, Section
from docscriptor.components.generated import ReferencesPage, TableOfContents
from docscriptor.components.inline import InlineInput, Text, bold
from docscriptor.components.people import AuthorInput, AuthorLayout
from docscriptor.components.references import CitationLibrary, CitationSource
from docscriptor.document import Document
from docscriptor.layout.theme import (
    BlockOptions,
    CaptionOptions,
    GeneratedPageOptions,
    HeadingNumbering,
    PageNumberOptions,
    Theme,
    TitleMatterOptions,
    TypographyOptions,
)
from docscriptor.settings import DocumentSettings, PageMargins, PageSize


AbstractInput = str | Paragraph | Sequence[BlockInput]


@dataclass(slots=True)
class ManuscriptSection:
    """A lightweight section descriptor accepted by article templates."""

    title: InlineInput
    children: Sequence[BlockInput] = ()
    level: int = 1
    numbered: bool = True

    def to_section(self) -> Section:
        """Return a concrete ``Section`` block."""

        return Section(
            self.title,
            *self.children,
            level=self.level,
            numbered=self.numbered,
        )


ArticleSectionInput = Section | ManuscriptSection | tuple[InlineInput, Sequence[BlockInput]]


@dataclass(slots=True)
class JournalArticleTemplate:
    """Build a document from title matter, abstract, body sections, and references."""

    name: str = "Journal article"
    theme: Theme = field(default_factory=Theme)
    page_size: PageSize = field(default_factory=PageSize.a4)
    page_margins: PageMargins = field(default_factory=PageMargins)
    author_layout: AuthorLayout = field(default_factory=AuthorLayout)
    include_contents: bool = False
    include_references: bool = True
    cover_page: bool = False

    def build(
        self,
        title: str,
        *,
        abstract: AbstractInput | None = None,
        sections: Sequence[ArticleSectionInput] = (),
        authors: Sequence[AuthorInput] | None = None,
        keywords: Sequence[str] | None = None,
        subtitle: InlineInput | None = None,
        summary: str | None = None,
        citations: CitationLibrary | Sequence[CitationSource] | str | None = None,
        include_contents: bool | None = None,
        include_references: bool | None = None,
        cover_page: bool | None = None,
    ) -> Document:
        """Build a ``Document`` from manuscript-shaped inputs."""

        include_contents_value = self.include_contents if include_contents is None else include_contents
        include_references_value = self.include_references if include_references is None else include_references

        children: list[BlockInput] = []
        if include_contents_value:
            children.append(TableOfContents(show_page_numbers=False, max_level=3))
        if abstract is not None:
            children.append(
                Section(
                    "Abstract",
                    *self._abstract_blocks(abstract),
                    level=1,
                    numbered=False,
                )
            )
        if keywords:
            children.append(
                Paragraph(
                    bold("Keywords: "),
                    Text(", ".join(keywords)),
                    space_after=18.0,
                    keep_with_next=True,
                )
            )
        children.extend(self._coerce_sections(sections))
        if include_references_value:
            children.append(ReferencesPage())

        settings = DocumentSettings(
            authors=authors,
            author_layout=self.author_layout,
            subtitle=subtitle,
            summary=summary or title,
            cover_page=self.cover_page if cover_page is None else cover_page,
            page_size=self.page_size,
            page_margins=self.page_margins,
            theme=self.theme,
        )
        return Document(title, *children, settings=settings, citations=citations)

    def _abstract_blocks(self, abstract: AbstractInput) -> list[BlockInput]:
        if isinstance(abstract, Paragraph):
            return [abstract]
        if isinstance(abstract, str):
            return [Paragraph(abstract)]
        return list(abstract)

    def _coerce_sections(self, sections: Sequence[ArticleSectionInput]) -> list[Section]:
        return [self._coerce_section(section) for section in sections]

    def _coerce_section(self, section: ArticleSectionInput) -> Section:
        if isinstance(section, Section):
            return section
        if isinstance(section, ManuscriptSection):
            return section.to_section()
        title, children = section
        return Chapter(title, *children)


def _article_numbering() -> HeadingNumbering:
    return HeadingNumbering(enabled=True, formats=("decimal", "decimal", "decimal"))


def _elsevier_theme() -> Theme:
    return Theme(
        TypographyOptions(
            body_font_name="Times New Roman",
            monospace_font_name="Courier New",
            title_font_size=18.0,
            body_font_size=10.0,
            heading_sizes=(14.0, 12.0, 11.0, 10.5),
            caption_font_size=9.0,
        ),
        CaptionOptions(
            caption_alignment="left",
            table_caption_position="above",
            figure_caption_position="below",
        ),
        GeneratedPageOptions(generated_section_level=1, generated_page_breaks=False),
        PageNumberOptions(show_page_numbers=True, page_number_alignment="center"),
        TitleMatterOptions(
            title_alignment="center",
            subtitle_alignment="center",
            author_alignment="center",
            affiliation_alignment="center",
            author_detail_alignment="center",
        ),
        BlockOptions(
            paragraph_alignment="justify",
            table_alignment="center",
            figure_alignment="center",
            heading_numbering=_article_numbering(),
        ),
    )


def _taylor_francis_theme() -> Theme:
    return Theme(
        TypographyOptions(
            body_font_name="Times New Roman",
            monospace_font_name="Courier New",
            title_font_size=17.0,
            body_font_size=10.5,
            heading_sizes=(13.5, 12.0, 11.0, 10.5),
            caption_font_size=9.5,
        ),
        CaptionOptions(
            caption_alignment="left",
            table_caption_position="above",
            figure_caption_position="below",
        ),
        GeneratedPageOptions(generated_section_level=1, generated_page_breaks=False),
        PageNumberOptions(show_page_numbers=True, page_number_alignment="center"),
        TitleMatterOptions(
            title_alignment="left",
            subtitle_alignment="left",
            author_alignment="left",
            affiliation_alignment="left",
            author_detail_alignment="left",
        ),
        BlockOptions(
            paragraph_alignment="justify",
            table_alignment="center",
            figure_alignment="center",
            heading_numbering=_article_numbering(),
        ),
    )


class ElsevierArticle(JournalArticleTemplate):
    """Article preset with Elsevier-like manuscript defaults."""

    def __init__(
        self,
        *,
        theme: Theme | None = None,
        page_margins: PageMargins | None = None,
        include_contents: bool = False,
        include_references: bool = True,
    ) -> None:
        super().__init__(
            name="Elsevier article",
            theme=theme or _elsevier_theme(),
            page_size=PageSize.a4(),
            page_margins=page_margins or PageMargins.symmetric(vertical=2.5, horizontal=2.5, unit="cm"),
            author_layout=AuthorLayout(mode="journal", show_details=False),
            include_contents=include_contents,
            include_references=include_references,
        )


class TaylorFrancisArticle(JournalArticleTemplate):
    """Article preset with Taylor & Francis-like manuscript defaults."""

    def __init__(
        self,
        *,
        theme: Theme | None = None,
        page_margins: PageMargins | None = None,
        include_contents: bool = False,
        include_references: bool = True,
    ) -> None:
        super().__init__(
            name="Taylor & Francis article",
            theme=theme or _taylor_francis_theme(),
            page_size=PageSize.a4(),
            page_margins=page_margins or PageMargins.symmetric(vertical=2.54, horizontal=2.54, unit="cm"),
            author_layout=AuthorLayout(mode="journal", show_details=False),
            include_contents=include_contents,
            include_references=include_references,
        )


__all__ = [
    "ElsevierArticle",
    "JournalArticleTemplate",
    "ManuscriptSection",
    "TaylorFrancisArticle",
]
