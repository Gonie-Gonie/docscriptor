"""Tables, figures, and related media components."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Mapping, Sequence, TYPE_CHECKING

from docscriptor.components.base import Block
from docscriptor.components.blocks import CellInput, Paragraph, coerce_cell
from docscriptor.core import (
    PathLike,
    format_counter_value,
    length_to_inches,
    normalize_color,
    normalize_length_unit,
    normalize_text_alignment,
    normalize_vertical_alignment,
)
from docscriptor.layout.theme import TableStyle, TextStyle, table_style_with_overrides

if TYPE_CHECKING:
    from docscriptor.components.inline import BlockReference, InlineInput
    from docscriptor.renderers.context import DocxRenderContext, HtmlRenderContext, PdfRenderContext


MediaPlacement = Literal["auto", "here", "float", "top", "bottom", "page"]
TableSplit = bool | Literal["auto"]
DEFAULT_LONG_TABLE_ROW_THRESHOLD = 12


def normalize_media_placement(value: str | None) -> MediaPlacement:
    """Normalize advanced table/figure placement options."""

    if value is None:
        return "auto"
    normalized = value.strip().lower()
    aliases = {
        "h": "here",
        "here": "here",
        "float": "float",
        "tbp": "float",
        "htbp": "float",
        "t": "top",
        "top": "top",
        "b": "bottom",
        "bottom": "bottom",
        "p": "page",
        "page": "page",
        "auto": "auto",
    }
    placement = aliases.get(normalized)
    if placement is None:
        raise ValueError(f"Unsupported media placement: {value!r}")
    return placement  # type: ignore[return-value]


def normalize_table_split(value: TableSplit) -> TableSplit:
    """Normalize table splitting policy."""

    if isinstance(value, bool):
        return value
    if value == "auto":
        return value
    raise ValueError("Table split must be True, False, or 'auto'")


@dataclass(slots=True)
class TableCellStyle:
    """Cell-level table styling that can be applied to cells, rows, or columns."""

    background_color: str | None = None
    text_color: str | None = None
    bold: bool | None = None
    italic: bool | None = None
    horizontal_alignment: str | None = None
    vertical_alignment: str | None = None

    def __post_init__(self) -> None:
        self.background_color = normalize_color(self.background_color)
        self.text_color = normalize_color(self.text_color)
        self.horizontal_alignment = (
            normalize_text_alignment(self.horizontal_alignment)
            if self.horizontal_alignment is not None
            else None
        )
        self.vertical_alignment = (
            normalize_vertical_alignment(self.vertical_alignment)
            if self.vertical_alignment is not None
            else None
        )

    def merged(self, *others: TableCellStyle | None) -> TableCellStyle:
        """Return a new style with later non-``None`` values overriding earlier ones."""

        merged = TableCellStyle(
            background_color=self.background_color,
            text_color=self.text_color,
            bold=self.bold,
            italic=self.italic,
            horizontal_alignment=self.horizontal_alignment,
            vertical_alignment=self.vertical_alignment,
        )
        for other in others:
            if other is None:
                continue
            for field_name in (
                "background_color",
                "text_color",
                "bold",
                "italic",
                "horizontal_alignment",
                "vertical_alignment",
            ):
                value = getattr(other, field_name)
                if value is not None:
                    setattr(merged, field_name, value)
        return merged

    def text_style(self) -> TextStyle:
        """Return the inline text defaults represented by this cell style."""

        return TextStyle(
            color=self.text_color,
            bold=self.bold,
            italic=self.italic,
        )


TableCellStyleInput = TableCellStyle | Mapping[str, object]


def coerce_table_cell_style(value: TableCellStyleInput) -> TableCellStyle:
    """Normalize a table cell style object or mapping."""

    if isinstance(value, TableCellStyle):
        return value
    if isinstance(value, Mapping):
        return TableCellStyle(**dict(value))
    raise TypeError(f"Unsupported table cell style: {type(value)!r}")


def _style_overrides(
    *,
    background_color: str | None = None,
    text_color: str | None = None,
    bold: bool | None = None,
    italic: bool | None = None,
    horizontal_alignment: str | None = None,
    vertical_alignment: str | None = None,
) -> TableCellStyle:
    return TableCellStyle(
        background_color=background_color,
        text_color=text_color,
        bold=bold,
        italic=italic,
        horizontal_alignment=horizontal_alignment,
        vertical_alignment=vertical_alignment,
    )


@dataclass(slots=True, init=False)
class TableCell:
    """A single table cell with optional row or column spanning."""

    content: Paragraph
    colspan: int
    rowspan: int
    background_color: str | None
    horizontal_alignment: str | None
    vertical_alignment: str | None
    style: TableCellStyle

    def __init__(
        self,
        value: CellInput,
        *,
        colspan: int = 1,
        rowspan: int = 1,
        style: TableCellStyleInput | None = None,
        background_color: str | None = None,
        text_color: str | None = None,
        bold: bool | None = None,
        italic: bool | None = None,
        horizontal_alignment: str | None = None,
        vertical_alignment: str | None = None,
    ) -> None:
        if colspan < 1:
            raise ValueError("TableCell.colspan must be >= 1")
        if rowspan < 1:
            raise ValueError("TableCell.rowspan must be >= 1")
        self.content = coerce_cell(value)
        self.colspan = colspan
        self.rowspan = rowspan
        base_style = (
            coerce_table_cell_style(style)
            if style is not None
            else TableCellStyle()
        )
        self.style = base_style.merged(
            _style_overrides(
                background_color=background_color,
                text_color=text_color,
                bold=bold,
                italic=italic,
                horizontal_alignment=horizontal_alignment,
                vertical_alignment=vertical_alignment,
            )
        )
        self.background_color = self.style.background_color
        self.horizontal_alignment = self.style.horizontal_alignment
        self.vertical_alignment = self.style.vertical_alignment


TableCellInput = TableCell | CellInput


def coerce_table_cell(value: TableCellInput) -> TableCell:
    """Normalize supported cell inputs into a ``TableCell`` instance."""

    if isinstance(value, TableCell):
        return value
    return TableCell(value)


def _is_nested_table_input(values: Sequence[object]) -> bool:
    if not values:
        return False
    return all(
        isinstance(item, Sequence) and not isinstance(item, (str, Paragraph, TableCell))
        for item in values
    )


def _coerce_table_matrix(
    values: Sequence[TableCellInput] | Sequence[Sequence[TableCellInput]],
) -> list[list[TableCell]]:
    items = list(values)
    if _is_nested_table_input(items):
        return [
            [coerce_table_cell(cell) for cell in row]
            for row in items
        ]  # type: ignore[arg-type]
    return [[coerce_table_cell(cell) for cell in items]]  # type: ignore[arg-type]


def _is_dataframe_like(value: object) -> bool:
    return hasattr(value, "columns") and (
        hasattr(value, "itertuples") or hasattr(value, "to_numpy")
    )


def _axis_labels(values: object) -> list[object]:
    if hasattr(values, "tolist"):
        return list(values.tolist())
    return list(values)


def _axis_names(values: object) -> tuple[str, ...]:
    names = getattr(values, "names", None)
    if names is not None:
        return tuple("" if name is None else str(name) for name in names)
    name = getattr(values, "name", None)
    return ("" if name is None else str(name),)


def _normalize_axis_values(values: object) -> list[tuple[str, ...]]:
    raw_values = _axis_labels(values)
    normalized: list[tuple[str, ...]] = []
    max_levels = (
        max(len(value) if isinstance(value, tuple) else 1 for value in raw_values)
        if raw_values
        else 1
    )
    for value in raw_values:
        if isinstance(value, tuple):
            parts = tuple("" if part is None else str(part) for part in value)
        else:
            parts = ("" if value is None else str(value),)
        normalized.append(parts + ("",) * (max_levels - len(parts)))
    return normalized


def _build_column_header_rows(column_values: list[tuple[str, ...]]) -> list[list[TableCell]]:
    if not column_values:
        return [[TableCell("")]]

    level_count = len(column_values[0])
    header_rows: list[list[TableCell]] = []
    for level in range(level_count):
        row: list[TableCell] = []
        column_index = 0
        while column_index < len(column_values):
            label = column_values[column_index][level]
            prefix = column_values[column_index][:level]
            if label == "":
                column_index += 1
                continue
            colspan = 1
            while (
                column_index + colspan < len(column_values)
                and column_values[column_index + colspan][level] == label
                and column_values[column_index + colspan][:level] == prefix
            ):
                colspan += 1
            rowspan = 1
            if all(
                all(part == "" for part in column_values[offset][level + 1 :])
                for offset in range(column_index, column_index + colspan)
            ):
                rowspan = level_count - level
            row.append(TableCell(label, colspan=colspan, rowspan=rowspan))
            column_index += colspan
        header_rows.append(row)
    return header_rows


def _build_row_header_cells(index_values: list[tuple[str, ...]]) -> list[list[TableCell]]:
    if not index_values:
        return []

    row_headers: list[list[TableCell]] = [[] for _ in index_values]
    level_count = len(index_values[0])
    for level in range(level_count):
        row_index = 0
        while row_index < len(index_values):
            label = index_values[row_index][level]
            prefix = index_values[row_index][:level]
            rowspan = 1
            while (
                row_index + rowspan < len(index_values)
                and index_values[row_index + rowspan][level] == label
                and index_values[row_index + rowspan][:level] == prefix
            ):
                rowspan += 1
            row_headers[row_index].append(TableCell(label, rowspan=rowspan))
            row_index += rowspan
    return row_headers


def _dataframe_body_rows(dataframe: object, *, include_index: bool) -> list[list[TableCell]]:
    if hasattr(dataframe, "itertuples"):
        data_rows = [tuple(row) for row in dataframe.itertuples(index=False, name=None)]
    else:
        matrix = dataframe.to_numpy().tolist()  # type: ignore[call-arg]
        data_rows = [tuple(row) for row in matrix]

    body_rows: list[list[TableCell]] = []
    if include_index:
        index_values = _normalize_axis_values(dataframe.index)
        row_headers = _build_row_header_cells(index_values)
        for row_index, row_values in enumerate(data_rows):
            body_rows.append(
                row_headers[row_index]
                + [TableCell("" if value is None else str(value)) for value in row_values]
            )
        return body_rows

    for row_values in data_rows:
        body_rows.append([TableCell("" if value is None else str(value)) for value in row_values])
    return body_rows


def _dataframe_header_rows(dataframe: object, *, include_index: bool) -> list[list[TableCell]]:
    column_values = _normalize_axis_values(dataframe.columns)
    header_rows = _build_column_header_rows(column_values)
    if not include_index:
        return header_rows

    index_names = _axis_names(dataframe.index)
    if header_rows:
        header_rows[0] = [
            TableCell(name, rowspan=len(header_rows))
            for name in index_names
        ] + header_rows[0]
        return header_rows
    return [[TableCell(name) for name in index_names]]


@dataclass(slots=True)
class TablePlacement:
    """A positioned cell inside a rectangular table layout."""

    row: int
    column: int
    cell: TableCell
    header: bool
    body_row_index: int | None = None


@dataclass(slots=True)
class TableLayout:
    """Expanded rectangular table layout used by renderers."""

    row_count: int
    column_count: int
    header_row_count: int
    placements: list[TablePlacement]


def build_table_layout(
    header_rows: Sequence[Sequence[TableCell]],
    body_rows: Sequence[Sequence[TableCell]],
) -> TableLayout:
    """Expand spanned cells into positioned placements for renderer output."""

    all_rows = [(True, row, None) for row in header_rows] + [
        (False, row, body_row_index)
        for body_row_index, row in enumerate(body_rows)
    ]
    active_rowspans: dict[int, int] = {}
    placements: list[TablePlacement] = []
    column_count = 0

    for row_index, (is_header, row_cells, body_row_index) in enumerate(all_rows):
        pending_rowspans = {
            column: remaining - 1
            for column, remaining in active_rowspans.items()
            if remaining > 1
        }
        rowspans_from_current: dict[int, int] = {}
        column_index = 0
        for cell in row_cells:
            while active_rowspans.get(column_index, 0) > 0:
                column_index += 1
            placements.append(
                TablePlacement(
                    row=row_index,
                    column=column_index,
                    cell=cell,
                    header=is_header,
                    body_row_index=body_row_index,
                )
            )
            for offset in range(cell.colspan):
                column = column_index + offset
                if active_rowspans.get(column, 0) > 0:
                    raise ValueError("Table cell spans overlap")
                if cell.rowspan > 1:
                    rowspans_from_current[column] = cell.rowspan - 1
            column_index += cell.colspan

        column_count = max(
            column_count,
            column_index,
            (max(active_rowspans.keys(), default=-1) + 1) if active_rowspans else 0,
        )
        active_rowspans = pending_rowspans | rowspans_from_current

    if active_rowspans:
        column_count = max(column_count, max(active_rowspans.keys(), default=-1) + 1)

    return TableLayout(
        row_count=len(all_rows),
        column_count=column_count,
        header_row_count=len(header_rows),
        placements=placements,
    )


def _coerce_style_mapping(
    styles: Mapping[int, TableCellStyleInput] | None,
    *,
    name: str,
) -> dict[int, TableCellStyle]:
    if styles is None:
        return {}
    normalized: dict[int, TableCellStyle] = {}
    for key, value in styles.items():
        index = int(key)
        if index < 0:
            raise ValueError(f"{name} indexes must be >= 0")
        normalized[index] = coerce_table_cell_style(value)
    return normalized


@dataclass(slots=True, init=False)
class Table(Block):
    """A table supporting explicit spans and dataframe-like inputs."""

    header_rows: list[list[TableCell]]
    rows: list[list[TableCell]]
    caption: Paragraph | None
    column_widths: list[float] | None
    unit: str | None
    identifier: str | None
    style: TableStyle
    include_index: bool
    split: TableSplit
    placement: MediaPlacement
    long_table_threshold: int | None
    row_styles: dict[int, TableCellStyle]
    column_styles: dict[int, TableCellStyle]
    header_row_styles: dict[int, TableCellStyle]

    def __init__(
        self,
        headers: Sequence[TableCellInput] | Sequence[Sequence[TableCellInput]] | object,
        rows: Sequence[Sequence[TableCellInput]] | None = None,
        *,
        caption: CellInput | None = None,
        column_widths: Sequence[float] | None = None,
        unit: str | None = None,
        identifier: str | None = None,
        style: TableStyle | None = None,
        header_background_color: str | None = None,
        header_text_color: str | None = None,
        border_color: str | None = None,
        body_background_color: str | None = None,
        alternate_row_background_color: str | None = None,
        cell_horizontal_alignment: str | None = None,
        cell_vertical_alignment: str | None = None,
        header_horizontal_alignment: str | None = None,
        header_vertical_alignment: str | None = None,
        cell_padding: float | None = None,
        include_index: bool = False,
        split: TableSplit = False,
        placement: str | None = None,
        long_table_threshold: int | None = None,
        row_styles: Mapping[int, TableCellStyleInput] | None = None,
        column_styles: Mapping[int, TableCellStyleInput] | None = None,
        header_row_styles: Mapping[int, TableCellStyleInput] | None = None,
    ) -> None:
        if rows is None and _is_dataframe_like(headers):
            dataframe = headers
            self.header_rows = _dataframe_header_rows(
                dataframe,
                include_index=include_index,
            )
            self.rows = _dataframe_body_rows(dataframe, include_index=include_index)
        else:
            if rows is None:
                raise ValueError(
                    "rows is required unless the first argument is a dataframe-like object"
                )
            self.header_rows = _coerce_table_matrix(headers)  # type: ignore[arg-type]
            self.rows = [
                [coerce_table_cell(cell) for cell in row]
                for row in rows
            ]

        self.caption = coerce_cell(caption) if caption is not None else None
        self.column_widths = list(column_widths) if column_widths is not None else None
        self.unit = normalize_length_unit(unit) if unit is not None else None
        self.identifier = identifier
        self.style = table_style_with_overrides(
            style,
            header_background_color=header_background_color,
            header_text_color=header_text_color,
            border_color=border_color,
            body_background_color=body_background_color,
            alternate_row_background_color=alternate_row_background_color,
            cell_horizontal_alignment=cell_horizontal_alignment,
            cell_vertical_alignment=cell_vertical_alignment,
            header_horizontal_alignment=header_horizontal_alignment,
            header_vertical_alignment=header_vertical_alignment,
            cell_padding=cell_padding,
        )
        self.include_index = include_index
        self.split = normalize_table_split(split)
        self.placement = normalize_media_placement(placement)
        if long_table_threshold is not None and long_table_threshold < 1:
            raise ValueError("long_table_threshold must be >= 1")
        self.long_table_threshold = long_table_threshold
        self.row_styles = _coerce_style_mapping(row_styles, name="row_styles")
        self.column_styles = _coerce_style_mapping(column_styles, name="column_styles")
        self.header_row_styles = _coerce_style_mapping(
            header_row_styles,
            name="header_row_styles",
        )

        layout = self.layout()
        if self.column_widths is not None and len(self.column_widths) != layout.column_count:
            raise ValueError("column_widths must match the expanded number of table columns")

    @property
    def headers(self) -> list[TableCell]:
        """Return the first header row for compatibility with older code."""

        return self.header_rows[0]

    def layout(self) -> TableLayout:
        """Return the renderer-facing table layout."""

        return build_table_layout(self.header_rows, self.rows)

    def row_count(self) -> int:
        """Return the total rendered row count, including headers."""

        return len(self.header_rows) + len(self.rows)

    def resolved_split(self, default_threshold: int = DEFAULT_LONG_TABLE_ROW_THRESHOLD) -> bool:
        """Return whether renderers should allow this table to split across pages."""

        if self.split is True:
            return True
        threshold = self.long_table_threshold or default_threshold
        return self.row_count() > threshold

    def resolved_placement(self, default_threshold: int = DEFAULT_LONG_TABLE_ROW_THRESHOLD) -> MediaPlacement:
        """Return the effective placement after split/long-table rules."""

        if self.split is True or self.resolved_split(default_threshold):
            return "here"
        if self.placement == "auto":
            return "float"
        return self.placement

    def effective_cell_style(self, placement: TablePlacement) -> TableCellStyle:
        """Return the resolved style for a rendered cell placement."""

        row_style = (
            self.header_row_styles.get(placement.row)
            if placement.header
            else (
                self.row_styles.get(placement.body_row_index)
                if placement.body_row_index is not None
                else None
            )
        )
        return self._base_cell_style(placement).merged(
            self.column_styles.get(placement.column),
            row_style,
            placement.cell.style,
        )

    def _base_cell_style(self, placement: TablePlacement) -> TableCellStyle:
        if placement.header:
            return TableCellStyle(
                background_color=self.style.header_background_color,
                text_color=self.style.header_text_color,
                bold=True,
                horizontal_alignment=self.style.header_horizontal_alignment,
                vertical_alignment=self.style.header_vertical_alignment,
            )

        background_color = self.style.body_background_color
        if (
            self.style.alternate_row_background_color is not None
            and placement.body_row_index is not None
            and placement.body_row_index % 2 == 1
        ):
            background_color = self.style.alternate_row_background_color
        return TableCellStyle(
            background_color=background_color,
            horizontal_alignment=self.style.cell_horizontal_alignment,
            vertical_alignment=self.style.cell_vertical_alignment,
        )

    def column_widths_in_inches(self, default_unit: str) -> list[float] | None:
        """Return column widths converted through the table or document unit."""

        if self.column_widths is None:
            return None
        unit = self.unit or default_unit
        return [length_to_inches(width, unit) for width in self.column_widths]

    @classmethod
    def from_dataframe(
        cls,
        dataframe: object,
        *,
        caption: CellInput | None = None,
        column_widths: Sequence[float] | None = None,
        unit: str | None = None,
        identifier: str | None = None,
        style: TableStyle | None = None,
        header_background_color: str | None = None,
        header_text_color: str | None = None,
        border_color: str | None = None,
        body_background_color: str | None = None,
        alternate_row_background_color: str | None = None,
        cell_horizontal_alignment: str | None = None,
        cell_vertical_alignment: str | None = None,
        header_horizontal_alignment: str | None = None,
        header_vertical_alignment: str | None = None,
        cell_padding: float | None = None,
        include_index: bool = False,
        split: TableSplit = False,
        placement: str | None = None,
        long_table_threshold: int | None = None,
        row_styles: Mapping[int, TableCellStyleInput] | None = None,
        column_styles: Mapping[int, TableCellStyleInput] | None = None,
        header_row_styles: Mapping[int, TableCellStyleInput] | None = None,
    ) -> Table:
        """Create a table directly from a dataframe-like object."""

        return cls(
            dataframe,
            caption=caption,
            column_widths=column_widths,
            unit=unit,
            identifier=identifier,
            style=style,
            header_background_color=header_background_color,
            header_text_color=header_text_color,
            border_color=border_color,
            body_background_color=body_background_color,
            alternate_row_background_color=alternate_row_background_color,
            cell_horizontal_alignment=cell_horizontal_alignment,
            cell_vertical_alignment=cell_vertical_alignment,
            header_horizontal_alignment=header_horizontal_alignment,
            header_vertical_alignment=header_vertical_alignment,
            cell_padding=cell_padding,
            include_index=include_index,
            split=split,
            placement=placement,
            long_table_threshold=long_table_threshold,
            row_styles=row_styles,
            column_styles=column_styles,
            header_row_styles=header_row_styles,
        )

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_table(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_table(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_table(self, context)


@dataclass(slots=True, init=False)
class Figure(Block):
    """An image block backed by a path or ``savefig()``-compatible object."""

    image_source: object
    caption: Paragraph | None
    width: float | None
    height: float | None
    unit: str | None
    identifier: str | None
    format: str
    dpi: int | None
    placement: MediaPlacement

    def __init__(
        self,
        image_source: PathLike | object,
        caption: CellInput | None = None,
        width: float | None = None,
        height: float | None = None,
        identifier: str | None = None,
        *,
        unit: str | None = None,
        format: str = "png",
        dpi: int | None = 150,
        placement: str | None = None,
    ) -> None:
        self.image_source = (
            Path(image_source)
            if isinstance(image_source, (str, Path))
            else image_source
        )
        self.caption = coerce_cell(caption) if caption is not None else None
        self.width = width
        self.height = height
        self.unit = normalize_length_unit(unit) if unit is not None else None
        self.identifier = identifier
        self.format = format
        self.dpi = dpi
        self.placement = normalize_media_placement(placement)

    def width_in_inches(self, default_unit: str) -> float | None:
        """Return figure width converted through the figure or document unit."""

        if self.width is None:
            return None
        return length_to_inches(self.width, self.unit or default_unit)

    def height_in_inches(self, default_unit: str) -> float | None:
        """Return figure height converted through the figure or document unit."""

        if self.height is None:
            return None
        return length_to_inches(self.height, self.unit or default_unit)

    def resolved_placement(self) -> MediaPlacement:
        """Return the effective placement for this figure."""

        if self.placement == "auto":
            return "float"
        return self.placement

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_figure(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_figure(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_figure(self, context)


@dataclass(slots=True, init=False)
class SubFigure:
    """A child image inside a numbered subfigure group."""

    image_source: object
    caption: Paragraph | None
    width: float | None
    height: float | None
    unit: str | None
    identifier: str | None
    format: str
    dpi: int | None
    label: str | None

    def __init__(
        self,
        image_source: PathLike | object,
        caption: CellInput | None = None,
        width: float | None = None,
        height: float | None = None,
        identifier: str | None = None,
        *,
        unit: str | None = None,
        format: str = "png",
        dpi: int | None = 150,
        label: str | None = None,
    ) -> None:
        self.image_source = (
            Path(image_source)
            if isinstance(image_source, (str, Path))
            else image_source
        )
        self.caption = coerce_cell(caption) if caption is not None else None
        self.width = width
        self.height = height
        self.unit = normalize_length_unit(unit) if unit is not None else None
        self.identifier = identifier
        self.format = format
        self.dpi = dpi
        self.label = label

    def width_in_inches(self, default_unit: str) -> float | None:
        """Return subfigure width converted through the subfigure or document unit."""

        if self.width is None:
            return None
        return length_to_inches(self.width, self.unit or default_unit)

    def height_in_inches(self, default_unit: str) -> float | None:
        """Return subfigure height converted through the subfigure or document unit."""

        if self.height is None:
            return None
        return length_to_inches(self.height, self.unit or default_unit)

    def reference(
        self,
        *label: InlineInput,
    ) -> BlockReference:
        """Create an explicit inline reference to this subfigure."""

        from docscriptor.components.inline import reference

        return reference(self, *label)


@dataclass(slots=True, init=False)
class SubFigureGroup(Block):
    """A numbered figure composed of labeled child figures."""

    subfigures: list[SubFigure]
    caption: Paragraph | None
    columns: int
    column_gap: float
    unit: str | None
    identifier: str | None
    placement: MediaPlacement
    label_format: str

    def __init__(
        self,
        *subfigures: SubFigure,
        caption: CellInput | None = None,
        columns: int = 2,
        column_gap: float = 0.18,
        unit: str | None = None,
        identifier: str | None = None,
        placement: str | None = None,
        label_format: str = "({label})",
    ) -> None:
        if not subfigures:
            raise ValueError("SubFigureGroup requires at least one SubFigure")
        if columns < 1:
            raise ValueError("SubFigureGroup.columns must be >= 1")
        if column_gap < 0:
            raise ValueError("SubFigureGroup.column_gap must be >= 0")
        if "{label}" not in label_format:
            raise ValueError("SubFigureGroup.label_format must contain '{label}'")
        self.subfigures = list(subfigures)
        self.caption = coerce_cell(caption) if caption is not None else None
        self.columns = columns
        self.column_gap = column_gap
        self.unit = normalize_length_unit(unit) if unit is not None else None
        self.identifier = identifier
        self.placement = normalize_media_placement(placement)
        self.label_format = label_format

    def label_for_index(self, index: int) -> str:
        """Return the raw subfigure label for a zero-based child index."""

        subfigure = self.subfigures[index]
        return subfigure.label or format_counter_value(index + 1, "lower-alpha")

    def formatted_label_for_index(self, index: int) -> str:
        """Return the display label for a zero-based child index."""

        return self.label_format.format(label=self.label_for_index(index))

    def resolved_placement(self) -> MediaPlacement:
        """Return the effective placement for this figure group."""

        if self.placement == "auto":
            return "float"
        return self.placement

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_subfigure_group(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_subfigure_group(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_subfigure_group(self, context)


__all__ = [
    "Figure",
    "MediaPlacement",
    "SubFigure",
    "SubFigureGroup",
    "Table",
    "TableCell",
    "TableCellInput",
    "TableCellStyle",
    "TableCellStyleInput",
    "TableLayout",
    "TablePlacement",
    "TableSplit",
    "build_table_layout",
    "coerce_table_cell",
    "coerce_table_cell_style",
    "normalize_media_placement",
    "normalize_table_split",
]
