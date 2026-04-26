"""Structured people and affiliation metadata for title matter."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from docscriptor.components.inline import Hyperlink, Text


@dataclass(slots=True)
class Affiliation:
    """Structured affiliation metadata for an author."""

    label: str | None = None
    department: str | None = None
    organization: str | None = None
    city: str | None = None
    country: str | None = None

    def __post_init__(self) -> None:
        if not any(
            (
                self.label,
                self.department,
                self.organization,
                self.city,
                self.country,
            )
        ):
            raise ValueError("Affiliation requires at least one populated field")

    def formatted(self) -> str:
        """Return a single-line affiliation label."""

        if self.label is not None:
            return self.label
        return ", ".join(
            part
            for part in (
                self.department,
                self.organization,
                self.city,
                self.country,
            )
            if part
        )


AffiliationInput = Affiliation | str


@dataclass(slots=True, frozen=True)
class AuthorTitleLine:
    """A typed title-matter line derived from a structured author."""

    kind: str
    fragments: tuple[Text, ...]

    def __post_init__(self) -> None:
        if self.kind not in {"name", "affiliation", "detail"}:
            raise ValueError(f"Unsupported author title line kind: {self.kind!r}")
        if not self.fragments:
            raise ValueError("AuthorTitleLine.fragments must not be empty")


@dataclass(slots=True, init=False)
class Author:
    """Structured author metadata for title matter and document metadata."""

    name: str
    affiliations: tuple[Affiliation, ...]
    email: str | None
    position: str | None
    corresponding: bool
    orcid: str | None
    note: str | None

    def __init__(
        self,
        name: str,
        *,
        affiliations: Sequence[AffiliationInput] | None = None,
        email: str | None = None,
        position: str | None = None,
        corresponding: bool = False,
        orcid: str | None = None,
        note: str | None = None,
    ) -> None:
        self.name = name
        self.affiliations = tuple(
            value if isinstance(value, Affiliation) else Affiliation(label=value)
            for value in (affiliations or ())
        )
        self.email = email
        self.position = position
        self.corresponding = corresponding
        self.orcid = orcid
        self.note = note

    def display_name(self) -> str:
        """Return the visible author label."""

        return f"{self.name}*" if self.corresponding else self.name

    def title_lines(self) -> tuple[AuthorTitleLine, ...]:
        """Return renderer-ready title-matter lines for this author."""

        lines: list[AuthorTitleLine] = [
            AuthorTitleLine(
                "name",
                (Text(self.display_name()),),
            )
        ]
        for affiliation in self.affiliations:
            lines.append(
                AuthorTitleLine(
                    "affiliation",
                    (Text(affiliation.formatted()),),
                )
            )
        detail = self._detail_fragments()
        if detail is not None:
            lines.append(AuthorTitleLine("detail", tuple(detail)))
        return tuple(lines)

    def _detail_fragments(self) -> list[Text] | None:
        fragments: list[Text] = []

        def append_separator() -> None:
            if fragments:
                fragments.append(Text(" | "))

        if self.position:
            append_separator()
            fragments.append(Text(self.position))
        if self.email:
            append_separator()
            fragments.append(Hyperlink.external(f"mailto:{self.email}", self.email))
        if self.orcid:
            append_separator()
            normalized_orcid = self.orcid.removeprefix("https://orcid.org/").strip("/")
            fragments.append(Text("ORCID "))
            fragments.append(
                Hyperlink.external(
                    f"https://orcid.org/{normalized_orcid}",
                    normalized_orcid,
                )
            )
        if self.note:
            append_separator()
            fragments.append(Text(self.note))
        return fragments or None


AuthorInput = Author | str


def coerce_authors(values: Sequence[AuthorInput] | None) -> tuple[Author, ...]:
    """Normalize simple author inputs into structured authors."""

    if values is None:
        return ()
    return tuple(
        value if isinstance(value, Author) else Author(str(value))
        for value in values
    )


__all__ = [
    "Affiliation",
    "AffiliationInput",
    "Author",
    "AuthorInput",
    "AuthorTitleLine",
    "coerce_authors",
]
