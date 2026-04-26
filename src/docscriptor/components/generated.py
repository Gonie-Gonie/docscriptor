"""Generated page blocks and document summaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from docscriptor.components.base import Block
from docscriptor.components.inline import InlineInput, Text, coerce_inlines

if TYPE_CHECKING:
    from docscriptor.renderers.context import DocxRenderContext, HtmlRenderContext, PdfRenderContext


@dataclass(slots=True, init=False)
class TableList(Block):
    """Generated list of captioned tables."""

    title: list[Text] | None

    def __init__(self, title: InlineInput | None = None) -> None:
        self.title = coerce_inlines((title,)) if title is not None else None

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_table_list(self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_table_list(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_table_list(self, context)


@dataclass(slots=True, init=False)
class FigureList(Block):
    """Generated list of captioned figures."""

    title: list[Text] | None

    def __init__(self, title: InlineInput | None = None) -> None:
        self.title = coerce_inlines((title,)) if title is not None else None

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_figure_list(self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_figure_list(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_figure_list(self, context)


@dataclass(slots=True, init=False)
class ReferencesPage(Block):
    """Generated reference list for cited bibliography entries."""

    title: list[Text] | None

    def __init__(self, title: InlineInput | None = None) -> None:
        self.title = coerce_inlines((title,)) if title is not None else None

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_references_page(self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_references_page(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_references_page(self, context)


@dataclass(slots=True, init=False)
class CommentsPage(Block):
    """Generated page listing numbered inline comments."""

    title: list[Text] | None

    def __init__(self, title: InlineInput | None = None) -> None:
        self.title = coerce_inlines((title,)) if title is not None else None

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_comments_page(self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_comments_page(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_comments_page(self, context)


@dataclass(slots=True, init=False)
class FootnotesPage(Block):
    """Generated page listing numbered portable footnotes."""

    title: list[Text] | None

    def __init__(self, title: InlineInput | None = None) -> None:
        self.title = coerce_inlines((title,)) if title is not None else None

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_footnotes_page(self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_footnotes_page(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_footnotes_page(self, context)


@dataclass(slots=True, init=False)
class TableOfContents(Block):
    """Generated outline of authored headings."""

    title: list[Text] | None

    def __init__(self, title: InlineInput | None = None) -> None:
        self.title = coerce_inlines((title,)) if title is not None else None

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_table_of_contents(self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_table_of_contents(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_table_of_contents(self, context)

__all__ = [
    "CommentsPage",
    "FigureList",
    "FootnotesPage",
    "ReferencesPage",
    "TableList",
    "TableOfContents",
]
