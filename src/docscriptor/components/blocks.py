"""Common structural and block-level document components."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import TYPE_CHECKING, Literal, Sequence

from docscriptor.components.base import Block, BlockInput, coerce_blocks
from docscriptor.components.equations import equation_plain_text
from docscriptor.components.inline import InlineInput, Text, coerce_inlines
from docscriptor.core import (
    length_to_inches,
    normalize_color,
    normalize_length_unit,
    normalize_text_alignment,
)
from docscriptor.layout.theme import (
    BoxStyle,
    ListStyle,
    ParagraphStyle,
    box_style_with_overrides,
    list_style_with_overrides,
    paragraph_style_with_overrides,
)

if TYPE_CHECKING:
    from docscriptor.renderers.context import DocxRenderContext, HtmlRenderContext, PdfRenderContext


CodeLanguagePosition = Literal["top-left", "top-right", "bottom-left", "bottom-right"]
MIN_SECTION_LEVEL = 1
MAX_SECTION_LEVEL = 6
DEFAULT_COUNTABLE_COUNTER = "countable"
THEOREM_COUNTER = "theorem"


@dataclass(slots=True, init=False)
class Paragraph(Block):
    """A paragraph built from inline fragments."""

    content: list[Text]
    style: ParagraphStyle

    def __init__(
        self,
        *content: InlineInput,
        style: ParagraphStyle | None = None,
        alignment: str | None = None,
        space_before: float | None = None,
        space_after: float | None = None,
        leading: float | None = None,
        left_indent: float | None = None,
        right_indent: float | None = None,
        first_line_indent: float | None = None,
        keep_together: bool | None = None,
        keep_with_next: bool | None = None,
        page_break_before: bool | None = None,
        widow_control: bool | None = None,
        unit: str | None = None,
    ) -> None:
        self.content = coerce_inlines(content)
        self.style = paragraph_style_with_overrides(
            style,
            alignment=alignment,
            space_before=space_before,
            space_after=space_after,
            leading=leading,
            left_indent=left_indent,
            right_indent=right_indent,
            first_line_indent=first_line_indent,
            keep_together=keep_together,
            keep_with_next=keep_with_next,
            page_break_before=page_break_before,
            widow_control=widow_control,
            unit=unit,
        )

    def plain_text(self) -> str:
        """Return the paragraph content without styling metadata."""

        return "".join(fragment.plain_text() for fragment in self.content)

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_paragraph(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_paragraph(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_paragraph(self, context)


ListInput = Paragraph | InlineInput


def coerce_list_item(value: ListInput) -> Paragraph:
    """Normalize a list item into a ``Paragraph`` instance."""

    if isinstance(value, Paragraph):
        return value
    return Paragraph(value)


@dataclass(slots=True, init=False)
class ListBlock(Block):
    """Shared implementation for bullet and ordered lists."""

    items: list[Paragraph]
    item_children: list[list["ListBlock"]]
    ordered: bool
    style: ListStyle | None

    def __init__(
        self,
        *items: ListInput,
        ordered: bool = False,
        style: ListStyle | None = None,
        marker_format: str | None = None,
        bullet: str | None = None,
        prefix: str | None = None,
        suffix: str | None = None,
        start: int | None = None,
        indent: float | None = None,
        marker_gap: float | None = None,
        item_children: Sequence[Sequence["ListBlock"]] | None = None,
    ) -> None:
        self.items = [coerce_list_item(item) for item in items if item is not None]
        if item_children is None:
            self.item_children = [[] for _ in self.items]
        else:
            self.item_children = [list(children) for children in item_children]
            if len(self.item_children) != len(self.items):
                raise ValueError("item_children must match the number of list items")
        self.ordered = ordered
        self.style = list_style_with_overrides(
            style,
            ordered=ordered,
            marker_format=marker_format,
            bullet=bullet,
            prefix=prefix,
            suffix=suffix,
            start=start,
            indent=indent,
            marker_gap=marker_gap,
        )

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_list(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_list(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_list(self, context)


class BulletList(ListBlock):
    """An unordered list of paragraph items."""

    def __init__(
        self,
        *items: ListInput,
        style: ListStyle | None = None,
        marker_format: str | None = None,
        bullet: str | None = None,
        prefix: str | None = None,
        suffix: str | None = None,
        start: int | None = None,
        indent: float | None = None,
        marker_gap: float | None = None,
        item_children: Sequence[Sequence[ListBlock]] | None = None,
    ) -> None:
        super().__init__(
            *items,
            ordered=False,
            style=style,
            marker_format=marker_format,
            bullet=bullet,
            prefix=prefix,
            suffix=suffix,
            start=start,
            indent=indent,
            marker_gap=marker_gap,
            item_children=item_children,
        )


class NumberedList(ListBlock):
    """An ordered list of paragraph items."""

    def __init__(
        self,
        *items: ListInput,
        style: ListStyle | None = None,
        marker_format: str | None = None,
        bullet: str | None = None,
        prefix: str | None = None,
        suffix: str | None = None,
        start: int | None = None,
        indent: float | None = None,
        marker_gap: float | None = None,
        item_children: Sequence[Sequence[ListBlock]] | None = None,
    ) -> None:
        super().__init__(
            *items,
            ordered=True,
            style=style,
            marker_format=marker_format,
            bullet=bullet,
            prefix=prefix,
            suffix=suffix,
            start=start,
            indent=indent,
            marker_gap=marker_gap,
            item_children=item_children,
        )


@dataclass(slots=True, init=False)
class CodeBlock(Block):
    """A preformatted code snippet."""

    code: str
    language: str | None
    show_language: bool
    language_position: CodeLanguagePosition
    style: ParagraphStyle

    def __init__(
        self,
        code: str,
        language: str | None = None,
        *,
        show_language: bool = True,
        language_position: CodeLanguagePosition = "top-right",
        style: ParagraphStyle | None = None,
        alignment: str | None = None,
        space_before: float | None = None,
        space_after: float | None = None,
        leading: float | None = None,
        left_indent: float | None = None,
        right_indent: float | None = None,
        first_line_indent: float | None = None,
        keep_together: bool | None = None,
        keep_with_next: bool | None = None,
        page_break_before: bool | None = None,
        widow_control: bool | None = None,
        unit: str | None = None,
    ) -> None:
        if language_position not in {"top-left", "top-right", "bottom-left", "bottom-right"}:
            raise ValueError("CodeBlock language_position must be top-left, top-right, bottom-left, or bottom-right")
        self.code = code
        self.language = language
        self.show_language = show_language
        self.language_position = language_position
        self.style = paragraph_style_with_overrides(
            style or ParagraphStyle(alignment="left", space_after=12.0),
            alignment=alignment,
            space_before=space_before,
            space_after=space_after,
            leading=leading,
            left_indent=left_indent,
            right_indent=right_indent,
            first_line_indent=first_line_indent,
            keep_together=keep_together,
            keep_with_next=keep_with_next,
            page_break_before=page_break_before,
            widow_control=widow_control,
            unit=unit,
        )

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_code_block(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_code_block(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_code_block(self, context)


@dataclass(slots=True, init=False)
class Equation(Block):
    """A centered block equation written in lightweight LaTeX syntax."""

    expression: str
    style: ParagraphStyle

    def __init__(
        self,
        expression: str,
        *,
        style: ParagraphStyle | None = None,
        alignment: str | None = None,
        space_before: float | None = None,
        space_after: float | None = None,
        leading: float | None = None,
        left_indent: float | None = None,
        right_indent: float | None = None,
        first_line_indent: float | None = None,
        keep_together: bool | None = None,
        keep_with_next: bool | None = None,
        page_break_before: bool | None = None,
        widow_control: bool | None = None,
        unit: str | None = None,
    ) -> None:
        self.expression = expression
        self.style = paragraph_style_with_overrides(
            style or ParagraphStyle(alignment="center", space_after=12.0),
            alignment=alignment,
            space_before=space_before,
            space_after=space_after,
            leading=leading,
            left_indent=left_indent,
            right_indent=right_indent,
            first_line_indent=first_line_indent,
            keep_together=keep_together,
            keep_with_next=keep_with_next,
            page_break_before=page_break_before,
            widow_control=widow_control,
            unit=unit,
        )

    def plain_text(self) -> str:
        """Return a readable plain-text equation approximation."""

        return equation_plain_text(self.expression)

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_equation(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_equation(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_equation(self, context)


@dataclass(slots=True)
class PageBreak(Block):
    """An explicit page break in the document flow."""

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_page_break(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_page_break(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_page_break(self, context)


@dataclass(slots=True, init=False)
class VerticalSpace(Block):
    """A vertical spacer in the document flow."""

    height: float
    unit: str

    def __init__(self, height: float = 12.0, *, unit: str = "pt") -> None:
        if height < 0:
            raise ValueError("VerticalSpace height must be >= 0")
        self.height = float(height)
        self.unit = normalize_length_unit(unit)

    def height_in_points(self) -> float:
        """Return the spacer height in typographic points."""

        return length_to_inches(self.height, self.unit) * 72.0

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_vertical_space(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_vertical_space(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_vertical_space(self, context)


@dataclass(slots=True, init=False)
class Divider(Block):
    """A horizontal divider similar to Notion's separator block."""

    color: str
    thickness: float
    space_before: float
    space_after: float
    width: float | None
    alignment: str
    unit: str | None

    def __init__(
        self,
        *,
        color: str = "DADDE3",
        thickness: float = 0.75,
        space_before: float = 8.0,
        space_after: float = 8.0,
        width: float | None = None,
        alignment: str = "center",
        unit: str | None = None,
    ) -> None:
        if thickness <= 0:
            raise ValueError("Divider thickness must be > 0")
        if space_before < 0:
            raise ValueError("Divider space_before must be >= 0")
        if space_after < 0:
            raise ValueError("Divider space_after must be >= 0")
        if width is not None and width < 0:
            raise ValueError("Divider width must be >= 0")
        normalized_alignment = normalize_text_alignment(alignment)
        if normalized_alignment == "justify":
            raise ValueError("Divider alignment must be left, center, or right")
        self.color = normalize_color(color) or "DADDE3"
        self.thickness = float(thickness)
        self.space_before = float(space_before)
        self.space_after = float(space_after)
        self.width = float(width) if width is not None else None
        self.alignment = normalized_alignment
        self.unit = normalize_length_unit(unit) if unit is not None else None

    def width_in_inches(self, default_unit: str) -> float | None:
        """Return the optional rule width in inches."""

        if self.width is None:
            return None
        return length_to_inches(self.width, self.unit or default_unit)

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_divider(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_divider(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_divider(self, context)


@dataclass(slots=True, init=False)
class ColumnSpan(Block):
    """Full-width content inside a ``MultiColumn`` block."""

    children: list[Block]

    def __init__(self, *children: BlockInput) -> None:
        self.children = coerce_blocks(children)

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_column_span(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_column_span(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_column_span(self, context)


@dataclass(slots=True, init=False)
class MultiColumn(Block):
    """A document flow container rendered across multiple columns."""

    children: list[Block]
    columns: int
    column_gap: float
    unit: str | None
    span_wide_media: bool

    def __init__(
        self,
        *children: BlockInput,
        columns: int = 2,
        column_gap: float = 0.25,
        unit: str | None = None,
        span_wide_media: bool = True,
    ) -> None:
        if columns < 1:
            raise ValueError("MultiColumn columns must be >= 1")
        if column_gap < 0:
            raise ValueError("MultiColumn column_gap must be >= 0")
        self.children = coerce_blocks(children)
        self.columns = columns
        self.column_gap = float(column_gap)
        self.unit = normalize_length_unit(unit) if unit is not None else None
        self.span_wide_media = bool(span_wide_media)

    def column_gap_in_inches(self, default_unit: str) -> float:
        """Return the gap between columns in inches."""

        return length_to_inches(self.column_gap, self.unit or default_unit)

    def column_width_in_inches(self, available_width: float, default_unit: str) -> float:
        """Return the width available to a single column in inches."""

        if self.columns <= 1:
            return max(available_width, 0)
        total_gap = self.column_gap_in_inches(default_unit) * (self.columns - 1)
        return max((available_width - total_gap) / self.columns, 0)

    def _child_spans_columns(
        self,
        child: Block,
        *,
        available_width: float,
        default_unit: str,
    ) -> bool:
        if isinstance(child, (ColumnSpan, PageBreak)):
            return True
        if not self.span_wide_media or self.columns <= 1:
            return False

        from docscriptor.components.media import Figure, SubFigureGroup, Table

        column_width = self.column_width_in_inches(available_width, default_unit)
        if isinstance(child, Figure):
            figure_width = child.width_in_inches(default_unit)
            return figure_width is None or figure_width > column_width
        if isinstance(child, Table):
            column_widths = child.column_widths_in_inches(default_unit)
            return column_widths is None or sum(column_widths) > column_width
        if isinstance(child, SubFigureGroup):
            row = child.subfigures[: child.columns]
            if not row:
                return False
            widths = [subfigure.width_in_inches(default_unit) for subfigure in row]
            if any(width is None for width in widths):
                return True
            group_gap = length_to_inches(child.column_gap, child.unit or default_unit)
            group_width = sum(width for width in widths if width is not None)
            group_width += group_gap * max(len(row) - 1, 0)
            return group_width > column_width
        return False

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_multi_column(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_multi_column(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_multi_column(self, context)


@dataclass(slots=True, init=False)
class Part(Block):
    """Top-level document division rendered on its own separator page."""

    title: list[Text]
    children: list[Block]
    numbered: bool
    toc: bool
    level: int

    def __init__(
        self,
        title: InlineInput,
        *children: BlockInput,
        numbered: bool = True,
        toc: bool | None = None,
    ) -> None:
        self.title = coerce_inlines((title,))
        self.children = coerce_blocks(children)
        self.numbered = numbered
        self.toc = numbered if toc is None else bool(toc)
        self.level = 0

    def plain_title(self) -> str:
        """Return the title without styling metadata."""

        return "".join(fragment.plain_text() for fragment in self.title)

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_part(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_part(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_part(self, context)


@dataclass(slots=True, init=False)
class Box(Block):
    """Bordered container for grouped block content."""

    children: list[Block]
    title: list[Text] | None
    style: BoxStyle

    def __init__(
        self,
        *children: BlockInput,
        title: InlineInput | None = None,
        style: BoxStyle | None = None,
        border_color: str | None = None,
        background_color: str | None = None,
        title_background_color: str | None = None,
        title_text_color: str | None = None,
        border_width: float | None = None,
        padding: float | None = None,
        padding_top: float | None = None,
        padding_right: float | None = None,
        padding_bottom: float | None = None,
        padding_left: float | None = None,
        space_after: float | None = None,
        width: float | None = None,
        unit: str | None = None,
        alignment: str | None = None,
    ) -> None:
        self.children = coerce_blocks(children)
        self.title = coerce_inlines((title,)) if title is not None else None
        self.style = box_style_with_overrides(
            style,
            border_color=border_color,
            background_color=background_color,
            title_background_color=title_background_color,
            title_text_color=title_text_color,
            border_width=border_width,
            padding=padding,
            padding_top=padding_top,
            padding_right=padding_right,
            padding_bottom=padding_bottom,
            padding_left=padding_left,
            space_after=space_after,
            width=width,
            unit=unit,
            alignment=alignment,
        )

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_box(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_box(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_box(self, context)


@dataclass(slots=True, init=False)
class CountableBlock(Block):
    """A theorem-like block with document-wide numbering."""

    kind: str
    children: list[Block]
    title: list[Text] | None
    numbered: bool
    counter: str | None
    reference_label: str
    label_suffix: str

    def __init__(
        self,
        kind: str,
        *children: BlockInput,
        title: InlineInput | None = None,
        numbered: bool = True,
        counter: str | None = DEFAULT_COUNTABLE_COUNTER,
        reference_label: str | None = None,
        label_suffix: str = ".",
    ) -> None:
        normalized_kind = str(kind).strip()
        if not normalized_kind:
            raise ValueError("CountableBlock kind must not be empty")
        if not isinstance(label_suffix, str):
            raise TypeError("CountableBlock label_suffix must be a string")
        normalized_counter = None if counter is None else str(counter).strip()
        if numbered and not normalized_counter:
            raise ValueError("Numbered CountableBlock objects require a non-empty counter")
        normalized_reference_label = (
            normalized_kind
            if reference_label is None
            else str(reference_label).strip()
        )
        if not normalized_reference_label:
            raise ValueError("CountableBlock reference_label must not be empty")

        self.kind = normalized_kind
        self.children = coerce_blocks(children)
        self.title = coerce_inlines((title,)) if title is not None else None
        self.numbered = bool(numbered)
        self.counter = normalized_counter if self.numbered else None
        self.reference_label = normalized_reference_label
        self.label_suffix = label_suffix

    def heading_label(self, number: int | None) -> str:
        """Return the visible heading label, including punctuation."""

        if self.numbered and number is not None:
            return f"{self.kind} {number}{self.label_suffix}"
        return f"{self.kind}{self.label_suffix}"

    def reference_text(self, number: int) -> str:
        """Return the default inline reference label."""

        return f"{self.reference_label} {number}"

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_countable_block(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_countable_block(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_countable_block(self, context)


def countable_kind(
    kind: str,
    *,
    counter: str | None = DEFAULT_COUNTABLE_COUNTER,
    numbered: bool = True,
    reference_label: str | None = None,
    label_suffix: str = ".",
) -> type[CountableBlock]:
    """Create a reusable theorem-like block class without manual subclassing."""

    normalized_kind = str(kind).strip()
    if not normalized_kind:
        raise ValueError("countable_kind kind must not be empty")

    class CustomCountableBlock(CountableBlock):
        def __init__(
            self,
            *children: BlockInput,
            title: InlineInput | None = None,
            numbered: bool = numbered,
            counter: str | None = counter,
            reference_label: str | None = reference_label,
            label_suffix: str = label_suffix,
        ) -> None:
            super().__init__(
                normalized_kind,
                *children,
                title=title,
                numbered=numbered,
                counter=counter,
                reference_label=reference_label,
                label_suffix=label_suffix,
            )

    CustomCountableBlock.__name__ = _countable_class_name(normalized_kind)
    CustomCountableBlock.__qualname__ = CustomCountableBlock.__name__
    CustomCountableBlock.__module__ = __name__
    CustomCountableBlock.__doc__ = f"A preconfigured countable block for {normalized_kind}."
    return CustomCountableBlock


def _countable_class_name(kind: str) -> str:
    pieces = re.findall(r"[A-Za-z0-9]+", kind)
    name = "".join(piece[:1].upper() + piece[1:] for piece in pieces)
    if not name or name[0].isdigit():
        return "CustomCountableBlock"
    return name


Definition = countable_kind("Definition", counter=THEOREM_COUNTER)
Lemma = countable_kind("Lemma", counter=THEOREM_COUNTER)
Proposition = countable_kind("Proposition", counter=THEOREM_COUNTER)
Theorem = countable_kind("Theorem", counter=THEOREM_COUNTER)
Corollary = countable_kind("Corollary", counter=THEOREM_COUNTER)
Proof = countable_kind("Proof", numbered=False, counter=None)
Example = countable_kind("Example", counter=THEOREM_COUNTER)
Remark = countable_kind("Remark", counter=THEOREM_COUNTER)
Assumption = countable_kind("Assumption", counter=THEOREM_COUNTER)
Axiom = countable_kind("Axiom", counter=THEOREM_COUNTER)
Claim = countable_kind("Claim", counter=THEOREM_COUNTER)
Conjecture = countable_kind("Conjecture", counter=THEOREM_COUNTER)


@dataclass(slots=True, init=False)
class Section(Block):
    """A titled section containing nested blocks."""

    title: list[Text]
    children: list[Block]
    level: int
    numbered: bool
    toc: bool

    def __init__(
        self,
        title: InlineInput,
        *children: BlockInput,
        level: int = 2,
        numbered: bool = True,
        toc: bool | None = None,
    ) -> None:
        if level < 1:
            raise ValueError("Section level must be >= 1")
        self.title = coerce_inlines((title,))
        self.children = coerce_blocks(children)
        self.level = level
        self.numbered = numbered
        self.toc = numbered if toc is None else bool(toc)

    def plain_title(self) -> str:
        """Return the title without styling metadata."""

        return "".join(fragment.plain_text() for fragment in self.title)

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.add_heading(
            container,
            self.title,
            self.level,
            context,
            number_label=(
                context.render_index.heading_number(self)
                if self.numbered
                else None
            ),
            anchor=context.render_index.heading_anchor(self),
            toc=self.toc,
        )
        for child in self.children:
            child.render_to_docx(renderer, container, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_section(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_section(self, context)


class Chapter(Section):
    """First-level document division."""

    def __init__(
        self,
        title: InlineInput,
        *children: BlockInput,
        numbered: bool = True,
        toc: bool | None = None,
    ) -> None:
        super().__init__(title, *children, level=1, numbered=numbered, toc=toc)


class Subsection(Section):
    """Third-level document division."""

    def __init__(
        self,
        title: InlineInput,
        *children: BlockInput,
        numbered: bool = True,
        toc: bool | None = None,
    ) -> None:
        super().__init__(title, *children, level=3, numbered=numbered, toc=toc)


class Subsubsection(Section):
    """Fourth-level document division."""

    def __init__(
        self,
        title: InlineInput,
        *children: BlockInput,
        numbered: bool = True,
        toc: bool | None = None,
    ) -> None:
        super().__init__(title, *children, level=4, numbered=numbered, toc=toc)


def section_for_level(
    title: InlineInput,
    *children: BlockInput,
    level: int,
    numbered: bool = True,
    toc: bool | None = None,
    min_level: int = MIN_SECTION_LEVEL,
    max_level: int = MAX_SECTION_LEVEL,
) -> Section:
    """Create the section-like object that best matches a heading level."""

    _validate_section_level(level, min_level=min_level, max_level=max_level)
    if level == 1:
        return Chapter(title, *children, numbered=numbered, toc=toc)
    if level == 3:
        return Subsection(title, *children, numbered=numbered, toc=toc)
    if level == 4:
        return Subsubsection(title, *children, numbered=numbered, toc=toc)
    return Section(title, *children, level=level, numbered=numbered, toc=toc)


def shift_heading_levels(
    blocks: Sequence[Block],
    delta: int,
    *,
    min_level: int = MIN_SECTION_LEVEL,
    max_level: int = MAX_SECTION_LEVEL,
) -> list[Block]:
    """Return blocks with section heading levels shifted by ``delta``.

    Paragraphs and non-heading blocks are returned unchanged. Section-like
    blocks are rebuilt at their new levels, and nested section children are
    shifted recursively.
    """

    return [
        shift_heading_level(
            block,
            delta,
            min_level=min_level,
            max_level=max_level,
        )
        for block in blocks
    ]


def shift_heading_level(
    block: Block,
    delta: int,
    *,
    min_level: int = MIN_SECTION_LEVEL,
    max_level: int = MAX_SECTION_LEVEL,
) -> Block:
    """Return one block with section heading levels shifted by ``delta``."""

    if not isinstance(block, Section):
        return block

    shifted_level = block.level + delta
    _validate_section_level(shifted_level, min_level=min_level, max_level=max_level)
    shifted_children = shift_heading_levels(
        block.children,
        delta,
        min_level=min_level,
        max_level=max_level,
    )
    return section_for_level(
        block.title,
        shifted_children,
        level=shifted_level,
        numbered=block.numbered,
        toc=block.toc,
        min_level=min_level,
        max_level=max_level,
    )


def _validate_section_level(
    level: int,
    *,
    min_level: int,
    max_level: int,
) -> None:
    if min_level < 1:
        raise ValueError("min_level must be >= 1 for section headings")
    if max_level < min_level:
        raise ValueError("max_level must be >= min_level")
    if level < min_level or level > max_level:
        raise ValueError(
            f"Heading level {level} is outside the supported range "
            f"{min_level}..{max_level}"
        )


CellInput = Paragraph | InlineInput


def coerce_cell(value: CellInput) -> Paragraph:
    """Normalize table or figure caption content into a ``Paragraph``."""

    if isinstance(value, Paragraph):
        return value
    return Paragraph(value)


__all__ = [
    "Box",
    "BulletList",
    "Chapter",
    "CellInput",
    "CodeBlock",
    "ColumnSpan",
    "CountableBlock",
    "DEFAULT_COUNTABLE_COUNTER",
    "Definition",
    "Divider",
    "Equation",
    "Example",
    "MAX_SECTION_LEVEL",
    "MIN_SECTION_LEVEL",
    "Lemma",
    "MultiColumn",
    "NumberedList",
    "PageBreak",
    "Paragraph",
    "Part",
    "Proof",
    "Remark",
    "Section",
    "Subsection",
    "Subsubsection",
    "THEOREM_COUNTER",
    "VerticalSpace",
    "Assumption",
    "Axiom",
    "Claim",
    "Conjecture",
    "Corollary",
    "Theorem",
    "Proposition",
    "coerce_cell",
    "coerce_list_item",
    "countable_kind",
    "section_for_level",
    "shift_heading_level",
    "shift_heading_levels",
]
