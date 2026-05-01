"""Public style objects and theme configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from docscriptor.core import (
    format_counter_value,
    normalize_color,
    normalize_counter_format,
    normalize_length_unit,
)


@dataclass(slots=True)
class TextStyle:
    """Inline text styling overrides.

    Each field is optional so styles can be layered and merged.
    """

    font_name: str | None = None
    font_size: float | None = None
    color: str | None = None
    highlight_color: str | None = None
    bold: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    strikethrough: bool | None = None

    def __post_init__(self) -> None:
        self.color = normalize_color(self.color)
        self.highlight_color = normalize_color(self.highlight_color)

    def merged(self, *others: TextStyle | None) -> TextStyle:
        """Return a new style with later values overriding earlier ones."""

        merged = TextStyle(
            font_name=self.font_name,
            font_size=self.font_size,
            color=self.color,
            highlight_color=self.highlight_color,
            bold=self.bold,
            italic=self.italic,
            underline=self.underline,
            strikethrough=self.strikethrough,
        )
        for other in others:
            if other is None:
                continue
            for field_name in (
                "font_name",
                "font_size",
                "color",
                "highlight_color",
                "bold",
                "italic",
                "underline",
                "strikethrough",
            ):
                value = getattr(other, field_name)
                if value is not None:
                    setattr(merged, field_name, value)
        return merged


@dataclass(slots=True)
class ParagraphStyle:
    """Block-level paragraph spacing and alignment settings."""

    alignment: str = "justify"
    space_after: float | None = 12.0
    leading: float | None = None
    left_indent: float | None = None
    right_indent: float | None = None
    first_line_indent: float | None = None

    def __post_init__(self) -> None:
        if self.alignment not in {"left", "center", "right", "justify"}:
            raise ValueError(f"Unsupported alignment: {self.alignment!r}")
        if self.left_indent is not None and self.left_indent < 0:
            raise ValueError("ParagraphStyle.left_indent must be >= 0")
        if self.right_indent is not None and self.right_indent < 0:
            raise ValueError("ParagraphStyle.right_indent must be >= 0")

    @classmethod
    def hanging(
        cls,
        left: float = 0.5,
        *,
        by: float | None = None,
        alignment: str = "justify",
        space_after: float | None = 12.0,
        leading: float | None = None,
    ) -> ParagraphStyle:
        """Create a hanging-indent paragraph style using inch values."""

        hanging_by = left if by is None else by
        if hanging_by < 0:
            raise ValueError("ParagraphStyle.hanging by must be >= 0")
        return cls(
            alignment=alignment,
            space_after=space_after,
            leading=leading,
            left_indent=left,
            first_line_indent=-hanging_by,
        )


@dataclass(slots=True)
class HeadingNumbering:
    """Configurable hierarchical numbering for authored headings."""

    enabled: bool = True
    formats: tuple[str, ...] = ("decimal", "decimal", "decimal", "decimal")
    separator: str = "."
    prefix: str = ""
    suffix: str = ""

    def __post_init__(self) -> None:
        self.formats = tuple(normalize_counter_format(value) for value in self.formats)
        if not self.formats:
            raise ValueError("HeadingNumbering.formats must not be empty")

    def format_label(self, counters: Sequence[int]) -> str | None:
        """Render a heading label such as ``1.2.3`` from nested counters."""

        if not self.enabled:
            return None

        pieces = [
            format_counter_value(value, self.formats[min(index, len(self.formats) - 1)])
            for index, value in enumerate(counters)
        ]
        return f"{self.prefix}{self.separator.join(pieces)}{self.suffix}"


@dataclass(slots=True)
class ListStyle:
    """Marker formatting for bullet and ordered lists."""

    marker_format: str = "decimal"
    bullet: str = "\u2022"
    prefix: str = ""
    suffix: str = "."
    start: int = 1
    indent: float = 0.25
    marker_gap: float = 0.1

    def __post_init__(self) -> None:
        self.marker_format = normalize_counter_format(self.marker_format)
        if self.start < 1:
            raise ValueError("ListStyle.start must be >= 1")
        if self.indent < 0:
            raise ValueError("ListStyle.indent must be >= 0")
        if self.marker_gap < 0:
            raise ValueError("ListStyle.marker_gap must be >= 0")

    def marker_for(self, index: int) -> str:
        """Return the rendered marker for a zero-based list item index."""

        if self.marker_format == "none":
            return ""

        marker_value = format_counter_value(
            index + self.start,
            self.marker_format,
            bullet=self.bullet,
        )
        return f"{self.prefix}{marker_value}{self.suffix}"


@dataclass(slots=True)
class BoxStyle:
    """Shared box styling for visually grouped content."""

    border_color: str = "B7C2D0"
    background_color: str = "F7FAFC"
    title_background_color: str | None = None
    title_text_color: str | None = None
    border_width: float = 0.75
    padding: float = 6.0
    padding_top: float | None = None
    padding_right: float | None = None
    padding_bottom: float | None = None
    padding_left: float | None = None
    space_after: float = 12.0
    width: float | None = None
    unit: str | None = None
    alignment: str | None = None

    def __post_init__(self) -> None:
        self.border_color = normalize_color(self.border_color) or "B7C2D0"
        self.background_color = normalize_color(self.background_color) or "F7FAFC"
        self.title_background_color = normalize_color(self.title_background_color)
        self.title_text_color = normalize_color(self.title_text_color)
        self.unit = normalize_length_unit(self.unit) if self.unit is not None else None
        if self.border_width < 0:
            raise ValueError("BoxStyle.border_width must be >= 0")
        if self.padding < 0:
            raise ValueError("BoxStyle.padding must be >= 0")
        for field_name in ("padding_top", "padding_right", "padding_bottom", "padding_left"):
            value = getattr(self, field_name)
            if value is not None and value < 0:
                raise ValueError(f"BoxStyle.{field_name} must be >= 0")
        if self.space_after < 0:
            raise ValueError("BoxStyle.space_after must be >= 0")
        if self.width is not None and self.width <= 0:
            raise ValueError("BoxStyle.width must be > 0")
        if self.alignment is not None and self.alignment not in {"left", "center", "right"}:
            raise ValueError(f"Unsupported BoxStyle alignment: {self.alignment!r}")

    def resolved_padding(self) -> tuple[float, float, float, float]:
        """Return top, right, bottom, and left padding in points."""

        return (
            self.padding if self.padding_top is None else self.padding_top,
            self.padding if self.padding_right is None else self.padding_right,
            self.padding if self.padding_bottom is None else self.padding_bottom,
            self.padding if self.padding_left is None else self.padding_left,
        )


@dataclass(slots=True)
class TableStyle:
    """Renderer-neutral table styling options."""

    header_background_color: str = "E8EDF5"
    header_text_color: str = "000000"
    border_color: str = "B7C2D0"
    body_background_color: str | None = None
    alternate_row_background_color: str | None = None
    cell_padding: float = 5.0

    def __post_init__(self) -> None:
        self.header_background_color = normalize_color(self.header_background_color) or "E8EDF5"
        self.header_text_color = normalize_color(self.header_text_color) or "000000"
        self.border_color = normalize_color(self.border_color) or "B7C2D0"
        self.body_background_color = normalize_color(self.body_background_color)
        self.alternate_row_background_color = normalize_color(self.alternate_row_background_color)
        if self.cell_padding < 0:
            raise ValueError("TableStyle.cell_padding must be >= 0")


@dataclass(slots=True)
class Theme:
    """Document-wide renderer defaults."""

    page_background_color: str = "FFFFFF"
    body_font_name: str = "Times New Roman"
    monospace_font_name: str = "Courier New"
    title_font_size: float = 22.0
    body_font_size: float = 11.0
    heading_sizes: tuple[float, ...] = (18.0, 15.0, 13.0, 11.5)
    caption_font_size: float | None = None
    caption_alignment: str = "center"
    table_alignment: str = "center"
    figure_alignment: str = "center"
    box_alignment: str = "center"
    table_caption_position: str = "above"
    figure_caption_position: str = "below"
    table_label: str = "Table"
    figure_label: str = "Figure"
    list_of_tables_title: str = "List of Tables"
    list_of_figures_title: str = "List of Figures"
    comments_title: str = "Comments"
    footnotes_title: str = "Footnotes"
    references_title: str = "References"
    contents_title: str = "Contents"
    generated_section_level: int = 2
    generated_page_breaks: bool = True
    footnote_placement: str = "page"
    auto_footnotes_page: bool = True
    show_page_numbers: bool = False
    page_number_alignment: str = "center"
    page_number_format: str = "{page}"
    front_matter_page_number_format: str = "lower-roman"
    main_matter_page_number_format: str = "decimal"
    page_number_font_size: float = 9.0
    title_alignment: str = "center"
    subtitle_alignment: str = "center"
    author_alignment: str = "center"
    affiliation_alignment: str = "center"
    author_detail_alignment: str = "center"
    heading_numbering: HeadingNumbering = field(default_factory=HeadingNumbering)
    bullet_list_style: ListStyle = field(
        default_factory=lambda: ListStyle(marker_format="bullet", suffix="")
    )
    numbered_list_style: ListStyle = field(default_factory=ListStyle)

    def __post_init__(self) -> None:
        self.page_background_color = normalize_color(self.page_background_color) or "FFFFFF"
        if self.caption_alignment not in {"left", "center", "right", "justify"}:
            raise ValueError(
                f"Unsupported caption alignment: {self.caption_alignment!r}"
            )
        for field_name in (
            "table_alignment",
            "figure_alignment",
            "box_alignment",
        ):
            value = getattr(self, field_name)
            if value not in {"left", "center", "right"}:
                raise ValueError(f"Unsupported alignment for {field_name}: {value!r}")
        if self.table_caption_position not in {"above", "below"}:
            raise ValueError(
                "table_caption_position must be 'above' or 'below'"
            )
        if self.figure_caption_position not in {"above", "below"}:
            raise ValueError(
                "figure_caption_position must be 'above' or 'below'"
            )
        if self.footnote_placement not in {"page", "document"}:
            raise ValueError(
                "footnote_placement must be 'page' or 'document'"
            )
        if self.page_number_alignment not in {"left", "center", "right"}:
            raise ValueError(
                f"Unsupported page number alignment: {self.page_number_alignment!r}"
            )
        self.front_matter_page_number_format = normalize_counter_format(
            self.front_matter_page_number_format
        )
        self.main_matter_page_number_format = normalize_counter_format(
            self.main_matter_page_number_format
        )
        if "{page}" not in self.page_number_format:
            raise ValueError("page_number_format must contain a '{page}' placeholder")
        for field_name in (
            "title_alignment",
            "subtitle_alignment",
            "author_alignment",
            "affiliation_alignment",
            "author_detail_alignment",
        ):
            value = getattr(self, field_name)
            if value not in {"left", "center", "right", "justify"}:
                raise ValueError(f"Unsupported alignment for {field_name}: {value!r}")

    def heading_size(self, level: int) -> float:
        """Return the configured font size for a heading level."""

        index = min(max(level - 1, 0), len(self.heading_sizes) - 1)
        return self.heading_sizes[index]

    def heading_emphasis(self, level: int) -> tuple[bool, bool]:
        """Return ``(bold, italic)`` emphasis for the given heading level."""

        emphasis = (
            (True, False),
            (True, False),
            (True, True),
            (False, True),
        )
        index = min(max(level - 1, 0), len(emphasis) - 1)
        return emphasis[index]

    def heading_alignment(self, level: int) -> str:
        """Return the alignment to use for the given heading level."""

        return "left"

    def caption_size(self) -> float:
        """Return the effective caption font size."""

        return self.body_font_size if self.caption_font_size is None else self.caption_font_size

    def format_page_number(
        self,
        page_number: int,
        *,
        front_matter: bool = False,
    ) -> str:
        """Render the footer page number string for a page."""

        marker_format = (
            self.front_matter_page_number_format
            if front_matter
            else self.main_matter_page_number_format
        )
        page_label = format_counter_value(page_number, marker_format)
        return self.page_number_format.format(page=page_label)

    def format_heading_label(self, counters: Sequence[int]) -> str | None:
        """Render a heading numbering label for nested section counters."""

        return self.heading_numbering.format_label(counters)

    def list_style(self, *, ordered: bool) -> ListStyle:
        """Return the default style for bullet or ordered lists."""

        return self.numbered_list_style if ordered else self.bullet_list_style


__all__ = [
    "BoxStyle",
    "HeadingNumbering",
    "ListStyle",
    "ParagraphStyle",
    "TableStyle",
    "TextStyle",
    "Theme",
]
