"""User-facing configuration objects for documents and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from docscriptor.components.inline import InlineInput, Text, coerce_inlines
from docscriptor.components.people import Affiliation, Author, AuthorInput, AuthorTitleLine, coerce_authors
from docscriptor.layout.theme import (
    BoxStyle,
    HeadingNumbering,
    ListStyle,
    ParagraphStyle,
    TableStyle,
    TextStyle,
    Theme,
)


@dataclass(slots=True, init=False)
class DocumentSettings:
    """Document-level metadata and rendering configuration."""

    author: str | None
    summary: str | None
    subtitle: list[Text] | None
    authors: tuple[Author, ...]
    cover_page: bool
    theme: Theme

    def __init__(
        self,
        *,
        author: str | None = None,
        summary: str | None = None,
        subtitle: InlineInput | None = None,
        authors: Sequence[AuthorInput] | None = None,
        cover_page: bool = False,
        theme: Theme | None = None,
    ) -> None:
        self.author = author
        self.summary = summary
        self.subtitle = coerce_inlines((subtitle,)) if subtitle is not None else None
        self.authors = coerce_authors(authors)
        self.cover_page = cover_page
        self.theme = theme or Theme()

    def resolved_author(self) -> str | None:
        """Return the metadata author string used in file properties."""

        if self.author is not None:
            return self.author
        if not self.authors:
            return None
        return "; ".join(author.name for author in self.authors)

    def iter_author_title_lines(self) -> Iterable[tuple[AuthorTitleLine, bool]]:
        """Yield author title lines together with author-boundary markers."""

        for author in self.authors:
            lines = author.title_lines()
            for index, line in enumerate(lines):
                yield line, index == len(lines) - 1


__all__ = [
    "Affiliation",
    "Author",
    "BoxStyle",
    "DocumentSettings",
    "HeadingNumbering",
    "ListStyle",
    "ParagraphStyle",
    "TableStyle",
    "TextStyle",
    "Theme",
]
