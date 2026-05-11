"""Base block protocol and shared body container."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from docscriptor.components.inline import BlockReference, InlineInput
    from docscriptor.renderers.context import DocxRenderContext, HtmlRenderContext, PdfRenderContext


class Block:
    """Base class for block-level document objects."""

    def reference(
        self,
        *label: InlineInput,
    ) -> BlockReference:
        """Create an explicit inline reference to this block."""

        from docscriptor.components.inline import reference

        return reference(self, *label)

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        """Render the block into a DOCX container."""

        raise NotImplementedError

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        """Render the block into one or more PDF flowables."""

        raise NotImplementedError

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        """Render the block into HTML markup."""

        raise NotImplementedError


BlockInput = Block | str | Sequence["BlockInput"] | None


def coerce_blocks(values: Iterable[BlockInput]) -> list[Block]:
    """Normalize supported block inputs into block objects."""

    from docscriptor.components.blocks import Paragraph

    normalized: list[Block] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, Block):
            normalized.append(value)
            continue
        if isinstance(value, str):
            normalized.append(Paragraph(value))
            continue
        if isinstance(value, Sequence):
            normalized.extend(coerce_blocks(value))
            continue
        raise TypeError(f"Unsupported block value: {type(value)!r}")
    return normalized


@dataclass(slots=True, init=False)
class Body(Block):
    """Top-level block container used by ``Document``."""

    children: list[Block]

    def __init__(self, *children: BlockInput) -> None:
        self.children = coerce_blocks(children)

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        for child in self.children:
            child.render_to_docx(renderer, container, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        story: list[object] = []
        for child in self.children:
            story.extend(child.render_to_pdf(renderer, context))
        return story

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return "".join(child.render_to_html(renderer, context) for child in self.children)


__all__ = ["Block", "BlockInput", "Body", "coerce_blocks"]
