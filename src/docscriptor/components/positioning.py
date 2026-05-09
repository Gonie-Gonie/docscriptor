"""Positioned and inline drawing components."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal, TYPE_CHECKING

from docscriptor.components.base import Block
from docscriptor.components.inline import InlineInput, Text, coerce_inlines
from docscriptor.core import PathLike, normalize_color, normalize_length_unit

if TYPE_CHECKING:
    from docscriptor.renderers.context import DocxRenderContext, HtmlRenderContext, PdfRenderContext
    from docscriptor.settings import DocumentSettings


PositionAnchor = Literal["page", "margin", "content"] | str
PositionPlacement = Literal["absolute", "inline"]
ShapeKind = Literal["rect", "ellipse", "line"]
ImageFit = Literal["contain", "stretch"]


@dataclass(frozen=True, slots=True)
class PositionedBox:
    """Resolved page-relative box in inches."""

    item: PositionedItem
    x: float
    y: float
    width: float
    height: float


def _normalize_anchor(anchor: PositionAnchor) -> str:
    value = str(anchor).strip()
    if not value:
        raise ValueError("Position anchor must not be empty")
    if value == "content":
        return "margin"
    return value


@dataclass(slots=True, init=False)
class TextBox(Block):
    """Positioned or inline text box.

    Absolute coordinates are measured from the selected anchor's top-left
    corner. Built-in anchors are ``"page"`` and ``"margin"``; any other anchor
    name refers to a named ``Shape``.
    """

    content: list[Text]
    x: float
    y: float
    width: float
    height: float
    anchor: str
    placement: PositionPlacement
    align: str
    valign: str
    font_size: float | None
    unit: str | None
    z_index: int

    def __init__(
        self,
        *content: InlineInput,
        x: float = 0.0,
        y: float = 0.0,
        width: float,
        height: float,
        anchor: PositionAnchor = "page",
        placement: PositionPlacement = "absolute",
        align: str = "left",
        valign: str = "top",
        font_size: float | None = None,
        unit: str | None = None,
        z_index: int = 0,
    ) -> None:
        if placement not in {"absolute", "inline"}:
            raise ValueError(f"Unsupported TextBox placement: {placement!r}")
        if align not in {"left", "center", "right"}:
            raise ValueError(f"Unsupported TextBox alignment: {align!r}")
        if valign not in {"top", "middle", "bottom"}:
            raise ValueError(f"Unsupported TextBox vertical alignment: {valign!r}")
        if width < 0 or height < 0:
            raise ValueError("TextBox width and height must be >= 0")
        self.content = coerce_inlines(content)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.anchor = _normalize_anchor(anchor)
        self.placement = placement
        self.align = align
        self.valign = valign
        self.font_size = font_size
        self.unit = normalize_length_unit(unit) if unit is not None else None
        self.z_index = z_index

    def plain_text(self) -> str:
        """Return the textbox content without styling metadata."""

        return "".join(fragment.plain_text() for fragment in self.content)

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_text_box(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_text_box(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_text_box(self, context)


@dataclass(slots=True, init=False)
class Shape(Block):
    """A basic positioned or inline shape."""

    kind: ShapeKind
    x: float
    y: float
    width: float
    height: float
    anchor: str
    placement: PositionPlacement
    name: str | None
    stroke_color: str | None
    fill_color: str | None
    stroke_width: float
    unit: str | None
    z_index: int

    def __init__(
        self,
        kind: ShapeKind,
        *,
        x: float = 0.0,
        y: float = 0.0,
        width: float,
        height: float,
        anchor: PositionAnchor = "page",
        placement: PositionPlacement = "absolute",
        name: str | None = None,
        stroke_color: str | None = "000000",
        fill_color: str | None = None,
        stroke_width: float = 1.0,
        unit: str | None = None,
        z_index: int = 0,
    ) -> None:
        if kind not in {"rect", "ellipse", "line"}:
            raise ValueError(f"Unsupported shape kind: {kind!r}")
        if placement not in {"absolute", "inline"}:
            raise ValueError(f"Unsupported Shape placement: {placement!r}")
        if kind != "line" and (width < 0 or height < 0):
            raise ValueError("Shape width and height must be >= 0")
        if stroke_width < 0:
            raise ValueError("Shape stroke_width must be >= 0")
        if name is not None and not name.strip():
            raise ValueError("Shape name must not be empty")
        self.kind = kind
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.anchor = _normalize_anchor(anchor)
        self.placement = placement
        self.name = name.strip() if name is not None else None
        self.stroke_color = normalize_color(stroke_color)
        self.fill_color = normalize_color(fill_color)
        self.stroke_width = stroke_width
        self.unit = normalize_length_unit(unit) if unit is not None else None
        self.z_index = z_index

    @classmethod
    def rect(cls, *, width: float, height: float, **kwargs: object) -> Shape:
        return cls("rect", width=width, height=height, **kwargs)

    @classmethod
    def ellipse(cls, *, width: float, height: float, **kwargs: object) -> Shape:
        return cls("ellipse", width=width, height=height, **kwargs)

    @classmethod
    def line(cls, *, width: float, height: float, **kwargs: object) -> Shape:
        return cls("line", width=width, height=height, **kwargs)

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_shape(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_shape(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_shape(self, context)

    def plain_text(self) -> str:
        """Return the inline text contribution for the shape."""

        return ""


@dataclass(slots=True, init=False)
class ImageBox(Block):
    """A positioned or inline image."""

    image_source: object
    x: float
    y: float
    width: float
    height: float
    anchor: str
    placement: PositionPlacement
    fit: ImageFit
    format: str
    dpi: int | None
    unit: str | None
    z_index: int

    def __init__(
        self,
        image_source: PathLike | object,
        *,
        x: float = 0.0,
        y: float = 0.0,
        width: float,
        height: float,
        anchor: PositionAnchor = "page",
        placement: PositionPlacement = "absolute",
        fit: ImageFit = "contain",
        format: str = "png",
        dpi: int | None = 150,
        unit: str | None = None,
        z_index: int = 0,
    ) -> None:
        if placement not in {"absolute", "inline"}:
            raise ValueError(f"Unsupported ImageBox placement: {placement!r}")
        if width < 0 or height < 0:
            raise ValueError("ImageBox width and height must be >= 0")
        if fit not in {"contain", "stretch"}:
            raise ValueError(f"Unsupported ImageBox fit: {fit!r}")
        self.image_source = (
            Path(image_source)
            if isinstance(image_source, (str, Path))
            else image_source
        )
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.anchor = _normalize_anchor(anchor)
        self.placement = placement
        self.fit = fit
        self.format = format
        self.dpi = dpi
        self.unit = normalize_length_unit(unit) if unit is not None else None
        self.z_index = z_index

    def render_to_docx(
        self,
        renderer: object,
        container: object,
        context: DocxRenderContext,
    ) -> None:
        renderer.render_image_box(container, self, context)

    def render_to_pdf(
        self,
        renderer: object,
        context: PdfRenderContext,
    ) -> list[object]:
        return renderer.render_image_box(self, context)

    def render_to_html(
        self,
        renderer: object,
        context: HtmlRenderContext,
    ) -> str:
        return renderer.render_image_box(self, context)

    def plain_text(self) -> str:
        """Return the inline text contribution for the image."""

        return ""


PositionedItem = TextBox | Shape | ImageBox


def coerce_positioned_items(values: Iterable[PositionedItem] | None) -> tuple[PositionedItem, ...]:
    """Validate a sequence of page-positioned drawing items."""

    if values is None:
        return ()
    items = tuple(values)
    for item in items:
        if not isinstance(item, (TextBox, Shape, ImageBox)):
            raise TypeError(f"Unsupported page item: {type(item)!r}")
        if item.placement != "absolute":
            raise ValueError("Document page_items require placement='absolute'")
    _validate_shape_anchors(items)
    return items


def resolve_positioned_boxes(
    items: Iterable[PositionedItem],
    settings: DocumentSettings,
    default_unit: str,
) -> list[PositionedBox]:
    """Resolve item coordinates to page-relative inches."""

    item_list = tuple(items)
    _validate_shape_anchors(item_list)
    shape_indexes = {
        item.name: index
        for index, item in enumerate(item_list)
        if isinstance(item, Shape) and item.name is not None
    }
    resolved_by_index: dict[int, PositionedBox] = {}
    resolving: set[int] = set()

    def resolve_index(index: int) -> PositionedBox:
        existing = resolved_by_index.get(index)
        if existing is not None:
            return existing
        if index in resolving:
            raise ValueError("Shape anchors cannot form a cycle")
        resolving.add(index)
        item = item_list[index]
        if item.anchor in shape_indexes:
            target = resolve_index(shape_indexes[item.anchor])
            origin = (target.x, target.y)
        else:
            origin = _anchor_origin(item.anchor, settings)
        box = _resolve_positioned_box(item, origin, default_unit)
        resolved_by_index[index] = box
        resolving.remove(index)
        return box

    resolved = [resolve_index(index) for index in range(len(item_list))]
    return [
        box
        for _, box in sorted(
            enumerate(resolved),
            key=lambda indexed: (indexed[1].item.z_index, indexed[0]),
        )
    ]


def _validate_shape_anchors(items: tuple[PositionedItem, ...]) -> None:
    names: set[str] = set()
    for item in items:
        if isinstance(item, Shape) and item.name is not None:
            if item.name in names:
                raise ValueError(f"Duplicate shape name: {item.name!r}")
            names.add(item.name)
    for item in items:
        if item.anchor not in {"page", "margin"} and item.anchor not in names:
            raise ValueError(f"Unknown shape anchor: {item.anchor!r}")


def _resolve_positioned_box(
    item: PositionedItem,
    origin: tuple[float, float],
    default_unit: str,
) -> PositionedBox:
    origin_x, origin_y = origin
    unit = item.unit or default_unit
    from docscriptor.core import length_to_inches

    return PositionedBox(
        item=item,
        x=origin_x + length_to_inches(item.x, unit),
        y=origin_y + length_to_inches(item.y, unit),
        width=length_to_inches(item.width, unit),
        height=length_to_inches(item.height, unit),
    )


def _anchor_origin(
    anchor: str,
    settings: DocumentSettings,
) -> tuple[float, float]:
    if anchor == "page":
        return 0.0, 0.0
    if anchor == "margin":
        top, _, _, left = settings.page_margin_inches()
        return left, top
    raise ValueError(f"Unknown shape anchor: {anchor!r}")


__all__ = [
    "ImageBox",
    "ImageFit",
    "PositionAnchor",
    "PositionPlacement",
    "PositionedBox",
    "PositionedItem",
    "Shape",
    "ShapeKind",
    "TextBox",
    "coerce_positioned_items",
    "resolve_positioned_boxes",
]
