"""Layout, indexing, and theme support for renderers."""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "BoxStyle": "docscriptor.layout.theme",
    "CaptionEntry": "docscriptor.layout.indexing",
    "CitationOptions": "docscriptor.layout.theme",
    "CitationReferenceEntry": "docscriptor.layout.indexing",
    "CommentReferenceEntry": "docscriptor.layout.indexing",
    "FootnoteReferenceEntry": "docscriptor.layout.indexing",
    "HeadingEntry": "docscriptor.layout.indexing",
    "HeadingNumbering": "docscriptor.layout.theme",
    "ListStyle": "docscriptor.layout.theme",
    "ParagraphStyle": "docscriptor.layout.theme",
    "RenderIndex": "docscriptor.layout.indexing",
    "TableStyle": "docscriptor.layout.theme",
    "TextStyle": "docscriptor.layout.theme",
    "Theme": "docscriptor.layout.theme",
    "build_render_index": "docscriptor.layout.indexing",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> object:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
