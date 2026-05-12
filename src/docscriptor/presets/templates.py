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
    Theme,
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


__all__ = [
    "JournalArticleTemplate",
    "ManuscriptSection",
]
