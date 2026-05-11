"""Common structural and block-level document components."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from docscriptor.components.base import Block, BlockInput, coerce_blocks
from docscriptor.components.equations import equation_plain_text
from docscriptor.components.inline import InlineInput, Text, coerce_inlines
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
    ) -> None:
        self.items = [coerce_list_item(item) for item in items if item is not None]
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
        )


@dataclass(slots=True, init=False)
class CodeBlock(Block):
    """A preformatted code snippet."""

    code: str
    language: str | None
    style: ParagraphStyle

    def __init__(
        self,
        code: str,
        language: str | None = None,
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
        self.code = code
        self.language = language
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


PageBreaker = PageBreak


@dataclass(slots=True, init=False)
class Part(Block):
    """Top-level document division rendered on its own separator page."""

    title: list[Text]
    children: list[Block]
    numbered: bool
    level: int

    def __init__(
        self,
        title: InlineInput,
        *children: BlockInput,
        numbered: bool = True,
    ) -> None:
        self.title = coerce_inlines((title,))
        self.children = coerce_blocks(children)
        self.numbered = numbered
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
class Section(Block):
    """A titled section containing nested blocks."""

    title: list[Text]
    children: list[Block]
    level: int
    numbered: bool

    def __init__(
        self,
        title: InlineInput,
        *children: BlockInput,
        level: int = 2,
        numbered: bool = True,
    ) -> None:
        if level < 1:
            raise ValueError("Section level must be >= 1")
        self.title = coerce_inlines((title,))
        self.children = coerce_blocks(children)
        self.level = level
        self.numbered = numbered

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
            anchor=(
                context.render_index.heading_anchor(self)
                if self.numbered
                else None
            ),
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
    ) -> None:
        super().__init__(title, *children, level=1, numbered=numbered)


class Subsection(Section):
    """Third-level document division."""

    def __init__(
        self,
        title: InlineInput,
        *children: BlockInput,
        numbered: bool = True,
    ) -> None:
        super().__init__(title, *children, level=3, numbered=numbered)


class Subsubsection(Section):
    """Fourth-level document division."""

    def __init__(
        self,
        title: InlineInput,
        *children: BlockInput,
        numbered: bool = True,
    ) -> None:
        super().__init__(title, *children, level=4, numbered=numbered)


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
    "Equation",
    "NumberedList",
    "PageBreak",
    "PageBreaker",
    "Paragraph",
    "Part",
    "Section",
    "Subsection",
    "Subsubsection",
    "coerce_cell",
    "coerce_list_item",
]
