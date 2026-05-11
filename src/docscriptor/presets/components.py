"""Reusable styled components built from the core block primitives."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from docscriptor.components.base import BlockInput
from docscriptor.components.blocks import Box, CellInput
from docscriptor.components.media import Table, TableCellInput
from docscriptor.layout.theme import BoxStyle, TableStyle


_CALLOUT_VARIANTS: dict[str, dict[str, str]] = {
    "info": {
        "border_color": "3B82F6",
        "background_color": "EFF6FF",
        "title_background_color": "DBEAFE",
        "title_text_color": "1E3A8A",
    },
    "note": {
        "border_color": "64748B",
        "background_color": "F8FAFC",
        "title_background_color": "E2E8F0",
        "title_text_color": "0F172A",
    },
    "success": {
        "border_color": "16A34A",
        "background_color": "F0FDF4",
        "title_background_color": "DCFCE7",
        "title_text_color": "14532D",
    },
    "warning": {
        "border_color": "D97706",
        "background_color": "FFFBEB",
        "title_background_color": "FEF3C7",
        "title_text_color": "78350F",
    },
}


class CalloutBox(Box):
    """A titled box preset for notes, warnings, and reviewer-facing callouts."""

    def __init__(
        self,
        *children: BlockInput,
        title: CellInput | None = None,
        variant: str = "info",
        style: BoxStyle | None = None,
        **style_overrides: object,
    ) -> None:
        normalized_variant = variant.strip().lower()
        if normalized_variant not in _CALLOUT_VARIANTS:
            supported = ", ".join(sorted(_CALLOUT_VARIANTS))
            raise ValueError(f"Unsupported callout variant {variant!r}. Use one of: {supported}")
        base_style = style or BoxStyle(**_CALLOUT_VARIANTS[normalized_variant])
        display_title = title if title is not None else normalized_variant.title()
        super().__init__(
            *children,
            title=display_title,
            style=base_style,
            **style_overrides,
        )


class CompactTable(Table):
    """A denser table preset with smaller padding and subdued borders."""

    def __init__(
        self,
        headers: Sequence[TableCellInput] | Sequence[Sequence[TableCellInput]] | object,
        rows: Sequence[Sequence[TableCellInput]] | None = None,
        *,
        style: TableStyle | None = None,
        **table_options: object,
    ) -> None:
        super().__init__(
            headers,
            rows,
            style=style or TableStyle(
                header_background_color="F1F5F9",
                border_color="CBD5E1",
                cell_padding=3.0,
                border_width=0.4,
            ),
            **table_options,
        )


class KeyValueTable(CompactTable):
    """A two-column table preset for metadata, settings, and option lists."""

    def __init__(
        self,
        items: Mapping[object, object] | Sequence[tuple[object, object]],
        *,
        headers: tuple[str, str] = ("Field", "Value"),
        caption: CellInput | None = None,
        style: TableStyle | None = None,
        **table_options: object,
    ) -> None:
        pairs = items.items() if isinstance(items, Mapping) else items
        rows = [[str(key), str(value)] for key, value in pairs]
        super().__init__(
            headers,
            rows,
            caption=caption,
            style=style,
            **table_options,
        )


class PublicationTable(Table):
    """A manuscript-style table preset with light horizontal structure."""

    def __init__(
        self,
        headers: Sequence[TableCellInput] | Sequence[Sequence[TableCellInput]] | object,
        rows: Sequence[Sequence[TableCellInput]] | None = None,
        *,
        caption: CellInput | None = None,
        style: TableStyle | None = None,
        **table_options: object,
    ) -> None:
        super().__init__(
            headers,
            rows,
            caption=caption,
            style=style or TableStyle(
                header_background_color="FFFFFF",
                header_text_color="111827",
                border_color="6B7280",
                alternate_row_background_color="F9FAFB",
                cell_padding=4.0,
                border_width=0.35,
                repeat_header_rows=True,
            ),
            **table_options,
        )


def option_table(
    rows: Mapping[object, object] | Sequence[tuple[object, object]],
    *,
    caption: CellInput | None = None,
    **table_options: object,
) -> KeyValueTable:
    """Return a compact two-column table for documenting user-facing options."""

    return KeyValueTable(rows, headers=("Option", "Default or meaning"), caption=caption, **table_options)


def note_box(*children: BlockInput, title: CellInput | None = None, **style_options: object) -> CalloutBox:
    """Return an info callout box using the same options as ``CalloutBox``."""

    return CalloutBox(*children, title=title, variant="info", **style_options)


__all__ = [
    "CalloutBox",
    "CompactTable",
    "KeyValueTable",
    "PublicationTable",
    "note_box",
    "option_table",
]
