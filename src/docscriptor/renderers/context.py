"""Renderer context objects shared with block-level render dispatch."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from docscriptor.layout.indexing import RenderIndex
from docscriptor.layout.theme import Theme


@dataclass(slots=True)
class DocxRenderContext:
    """Context needed while rendering blocks into DOCX."""

    theme: Theme
    render_index: RenderIndex
    unit: str
    word_document: Any


@dataclass(slots=True)
class PdfRenderContext:
    """Context needed while rendering blocks into PDF."""

    theme: Theme
    render_index: RenderIndex
    unit: str
    styles: Any


@dataclass(slots=True)
class HtmlRenderContext:
    """Context needed while rendering blocks into HTML."""

    theme: Theme
    render_index: RenderIndex
    unit: str
