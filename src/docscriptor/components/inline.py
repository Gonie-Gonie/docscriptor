"""Inline authoring fragments and helper constructors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence, TYPE_CHECKING

from docscriptor.components.equations import equation_plain_text
from docscriptor.core import normalize_color
from docscriptor.layout.theme import TextStyle

if TYPE_CHECKING:
    from docscriptor.components.references import CitationSource


@dataclass(slots=True)
class Text:
    """Base inline text fragment.

    Args:
        value: Literal text content.
        style: Optional inline style overrides.
    """

    value: str
    style: TextStyle = field(default_factory=TextStyle)

    def plain_text(self) -> str:
        """Return the fragment without styling metadata."""

        return self.value

    @classmethod
    def styled(cls, value: str, **style_values: object) -> Text:
        """Create a plain text fragment with an inline ``TextStyle``."""

        return cls(value=value, style=TextStyle(**style_values))

    @classmethod
    def bold(cls, value: str, style: TextStyle | None = None) -> Bold:
        """Create a bold text fragment."""

        return Bold(value, style=style)

    @classmethod
    def italic(cls, value: str, style: TextStyle | None = None) -> Italic:
        """Create an italic text fragment."""

        return Italic(value, style=style)

    @classmethod
    def code(cls, value: str, style: TextStyle | None = None) -> Monospace:
        """Create a monospace text fragment."""

        return Monospace(value, style=style)

    @classmethod
    def color(
        cls,
        value: str,
        color: str,
        style: TextStyle | None = None,
    ) -> Text:
        """Create a colored text fragment."""

        return cls(
            value=value,
            style=TextStyle(color=color).merged(style),
        )

    @classmethod
    def highlight(
        cls,
        value: str,
        color: str = "FFFF00",
        style: TextStyle | None = None,
    ) -> Highlight:
        """Create a highlighted text fragment."""

        return Highlight(value, color=color, style=style)

    @classmethod
    def strikethrough(
        cls,
        value: str,
        style: TextStyle | None = None,
    ) -> Strikethrough:
        """Create a strikethrough text fragment."""

        return Strikethrough(value, style=style)

    @classmethod
    def from_markup(
        cls,
        source: str,
        *,
        style: TextStyle | None = None,
    ) -> list[Text]:
        """Parse simple markdown-like markup into inline fragments."""

        from docscriptor.components.markup import markup

        return markup(source, style=style)


class Bold(Text):
    """Bold inline text."""

    def __init__(self, value: str, style: TextStyle | None = None) -> None:
        super().__init__(value=value, style=TextStyle(bold=True).merged(style))


class Italic(Text):
    """Italic inline text."""

    def __init__(self, value: str, style: TextStyle | None = None) -> None:
        super().__init__(value=value, style=TextStyle(italic=True).merged(style))


class Monospace(Text):
    """Monospace inline text."""

    def __init__(self, value: str, style: TextStyle | None = None) -> None:
        super().__init__(
            value=value,
            style=TextStyle(font_name="Courier New").merged(style),
        )


Strong = Bold
Emphasis = Italic
Code = Monospace


_INLINE_CHIP_STYLE_FIELDS = (
    "background_color",
    "text_color",
    "border_color",
    "border_width",
    "padding_x",
    "padding_y",
    "radius",
    "font_size_delta",
    "font_name",
    "bold",
    "italic",
    "uppercase",
)


@dataclass(slots=True)
class InlineChipStyle:
    """Visual style for compact inline label chips.

    Padding and radius are expressed in em units so chips scale with the
    surrounding font. Border width and font size delta are expressed in points.
    """

    background_color: str = "E8F1FF"
    text_color: str = "1F3A5F"
    border_color: str | None = "A7C7E7"
    border_width: float = 0.5
    padding_x: float = 0.38
    padding_y: float = 0.12
    radius: float = 0.5
    font_size_delta: float = -0.5
    font_name: str | None = None
    bold: bool = True
    italic: bool = False
    uppercase: bool = False

    def __post_init__(self) -> None:
        self.background_color = normalize_color(self.background_color) or "E8F1FF"
        self.text_color = normalize_color(self.text_color) or "1F3A5F"
        self.border_color = normalize_color(self.border_color)
        if self.border_width < 0:
            raise ValueError("InlineChipStyle.border_width must be >= 0")
        if self.padding_x < 0:
            raise ValueError("InlineChipStyle.padding_x must be >= 0")
        if self.padding_y < 0:
            raise ValueError("InlineChipStyle.padding_y must be >= 0")
        if self.radius < 0:
            raise ValueError("InlineChipStyle.radius must be >= 0")

    def merged(self, **overrides: object) -> InlineChipStyle:
        values = {
            field_name: getattr(self, field_name)
            for field_name in _INLINE_CHIP_STYLE_FIELDS
        }
        for field_name, value in overrides.items():
            if field_name not in values:
                raise TypeError(f"Unsupported InlineChipStyle field: {field_name}")
            values[field_name] = value
        return InlineChipStyle(**values)


_DEFAULT_CHIP_STYLES = {
    "chip": InlineChipStyle(),
    "tag": InlineChipStyle(
        background_color="E8F1FF",
        text_color="1F3A5F",
        border_color="A7C7E7",
    ),
    "badge": InlineChipStyle(
        background_color="F3F4F6",
        text_color="1F2937",
        border_color="D1D5DB",
        padding_x=0.32,
    ),
    "status": InlineChipStyle(
        background_color="F3F4F6",
        text_color="374151",
        border_color="D1D5DB",
        uppercase=True,
    ),
    "keyboard": InlineChipStyle(
        background_color="F8FAFC",
        text_color="111827",
        border_color="CBD5E1",
        border_width=0.75,
        padding_x=0.28,
        padding_y=0.08,
        radius=0.22,
        font_size_delta=-0.5,
        font_name="Courier New",
        bold=False,
    ),
}

_STATUS_CHIP_STYLES = {
    "neutral": _DEFAULT_CHIP_STYLES["status"],
    "success": InlineChipStyle(
        background_color="ECFDF3",
        text_color="166534",
        border_color="BBF7D0",
        uppercase=True,
    ),
    "info": InlineChipStyle(
        background_color="E0F2FE",
        text_color="075985",
        border_color="BAE6FD",
        uppercase=True,
    ),
    "warning": InlineChipStyle(
        background_color="FEF3C7",
        text_color="92400E",
        border_color="FDE68A",
        uppercase=True,
    ),
    "danger": InlineChipStyle(
        background_color="FEE2E2",
        text_color="991B1B",
        border_color="FECACA",
        uppercase=True,
    ),
    "muted": InlineChipStyle(
        background_color="F3F4F6",
        text_color="374151",
        border_color="D1D5DB",
        uppercase=True,
    ),
}


class InlineChip(Text):
    """Compact inline visual token for tags, badges, status, and key labels."""

    __slots__ = ("chip_style", "kind")

    def __init__(
        self,
        value: object,
        *,
        chip_style: InlineChipStyle | None = None,
        kind: str = "chip",
        style: TextStyle | None = None,
    ) -> None:
        normalized_kind = _normalize_chip_kind(kind)
        super().__init__(value=str(value), style=style or TextStyle())
        self.chip_style = chip_style or _default_chip_style(normalized_kind)
        self.kind = normalized_kind

    def display_text(self) -> str:
        return self.value.upper() if self.chip_style.uppercase else self.value

    def plain_text(self) -> str:
        return self.display_text()


class Highlight(Text):
    """Highlighted inline text."""

    def __init__(
        self,
        value: str,
        *,
        color: str = "FFFF00",
        style: TextStyle | None = None,
    ) -> None:
        super().__init__(
            value=value,
            style=TextStyle(highlight_color=color).merged(style),
        )


class Strikethrough(Text):
    """Strikethrough inline text."""

    def __init__(self, value: str, style: TextStyle | None = None) -> None:
        super().__init__(
            value=value,
            style=TextStyle(strikethrough=True).merged(style),
        )


class LineBreak(Text):
    """Manual line break inside a paragraph."""

    def __init__(self) -> None:
        super().__init__(value="\n")

    def plain_text(self) -> str:
        """Return the line break as a newline in plain text."""

        return "\n"


class BlockReference(Text):
    """Inline reference to a numbered or anchored document object."""

    __slots__ = ("target", "label")

    def __init__(
        self,
        target: object,
        *label: InlineInput,
        style: TextStyle | None = None,
    ) -> None:
        super().__init__(value="", style=style or TextStyle())
        self.target = target
        self.label = coerce_inlines(label) if label else None

    def plain_text(self) -> str:
        """Return a placeholder reference string before numbering is resolved."""

        if self.label is not None:
            return "".join(fragment.plain_text() for fragment in self.label)
        return f"{_reference_label_prefix(self.target)} ?"


def _reference_label_prefix(target: object) -> str:
    target_name = type(target).__name__
    if target_name == "Table":
        return "Table"
    if target_name in {"Figure", "SubFigure", "SubFigureGroup"}:
        return "Figure"
    if target_name == "Equation":
        return "Equation"
    if target_name == "Paragraph":
        return "Paragraph"
    if target_name == "CodeBlock":
        return "Code block"
    if target_name == "Box":
        return "Box"
    if target_name == "Part":
        return "Part"
    if target_name in {"Chapter", "Section", "Subsection", "Subsubsection"}:
        return "Section"
    return type(target).__name__


def reference(
    target: object,
    *label: InlineInput,
    style: TextStyle | None = None,
) -> BlockReference:
    """Create an explicit inline reference to a document object."""

    if not _is_referenceable(target):
        raise TypeError(f"Unsupported reference target: {type(target)!r}")
    return BlockReference(target, *label, style=style)


class Citation(Text):
    """Inline citation rendered from a bibliography entry or key."""

    __slots__ = ("target",)

    def __init__(self, target: CitationSource | str, style: TextStyle | None = None) -> None:
        super().__init__(value="", style=style or TextStyle())
        self.target = target

    def plain_text(self) -> str:
        """Return a placeholder citation label."""

        return "[?]"

    @classmethod
    def reference(
        cls,
        target: CitationSource | str,
        *,
        style: TextStyle | None = None,
    ) -> Citation:
        """Create an inline citation fragment."""

        return cls(target, style=style)


def cite(target: CitationSource | str, *, style: TextStyle | None = None) -> Citation:
    """Compatibility helper for inline citation creation."""

    return Citation.reference(target, style=style)


class Hyperlink(Text):
    """Inline hyperlink to an external URL or internal anchor."""

    __slots__ = ("target", "label", "internal")

    def __init__(
        self,
        target: str,
        *label: InlineInput,
        internal: bool = False,
        style: TextStyle | None = None,
    ) -> None:
        super().__init__(
            value="",
            style=TextStyle(color="0563C1", underline=True).merged(style),
        )
        self.target = target
        self.label = coerce_inlines(label or (target,))
        self.internal = internal

    def plain_text(self) -> str:
        """Return the visible hyperlink label."""

        return "".join(fragment.plain_text() for fragment in self.label)

    @classmethod
    def external(
        cls,
        target: str,
        *label: InlineInput,
        style: TextStyle | None = None,
    ) -> Hyperlink:
        """Create an external hyperlink."""

        return cls(target, *label, internal=False, style=style)

    @classmethod
    def internal_anchor(
        cls,
        target: str,
        *label: InlineInput,
        style: TextStyle | None = None,
    ) -> Hyperlink:
        """Create an internal hyperlink."""

        return cls(target, *label, internal=True, style=style)


class Comment(Text):
    """Inline text annotated with a numbered comment."""

    __slots__ = ("comment", "author", "initials")

    def __init__(
        self,
        value: str,
        *comment: InlineInput,
        author: str | None = None,
        initials: str | None = None,
        style: TextStyle | None = None,
    ) -> None:
        super().__init__(value=value, style=style or TextStyle())
        self.comment = coerce_inlines(comment)
        self.author = author
        self.initials = initials

    def plain_text(self) -> str:
        """Return the visible inline text with a placeholder marker."""

        return f"{self.value}[?]"

    @classmethod
    def annotated(
        cls,
        value: str,
        *note: InlineInput,
        author: str | None = None,
        initials: str | None = None,
        style: TextStyle | None = None,
    ) -> Comment:
        """Create inline text with an attached numbered comment."""

        return cls(
            value,
            *note,
            author=author,
            initials=initials,
            style=style,
        )


def comment(
    value: str,
    *note: InlineInput,
    author: str | None = None,
    initials: str | None = None,
    style: TextStyle | None = None,
) -> Comment:
    """Compatibility helper for comment creation."""

    return Comment.annotated(
        value,
        *note,
        author=author,
        initials=initials,
        style=style,
    )


class Footnote(Text):
    """Inline text annotated with a numbered portable footnote."""

    __slots__ = ("note",)

    def __init__(
        self,
        value: str,
        *note: InlineInput,
        style: TextStyle | None = None,
    ) -> None:
        super().__init__(value=value, style=style or TextStyle())
        self.note = coerce_inlines(note)

    def plain_text(self) -> str:
        """Return the visible inline text with a placeholder marker."""

        return f"{self.value}[?]"

    @classmethod
    def annotated(
        cls,
        value: str,
        *note: InlineInput,
        style: TextStyle | None = None,
    ) -> Footnote:
        """Create inline text with an attached numbered footnote."""

        return cls(value, *note, style=style)


def footnote(
    value: str,
    *note: InlineInput,
    style: TextStyle | None = None,
) -> Footnote:
    """Compatibility helper for footnote creation."""

    return Footnote.annotated(value, *note, style=style)


class Math(Text):
    """Inline math fragment written in lightweight LaTeX syntax."""

    def __init__(self, value: str, style: TextStyle | None = None) -> None:
        super().__init__(value=value, style=TextStyle().merged(style))

    def plain_text(self) -> str:
        """Return a readable plain-text math approximation."""

        return equation_plain_text(self.value)

    @classmethod
    def inline(cls, value: str, *, style: TextStyle | None = None) -> Math:
        """Create an inline math fragment."""

        return cls(value, style=style)


def math(value: str, *, style: TextStyle | None = None) -> Math:
    """Compatibility helper for inline math creation."""

    return Math.inline(value, style=style)


def styled(value: str, **style_values: object) -> Text:
    """Compatibility helper for styled inline text."""

    return Text.styled(value, **style_values)


def bold(value: str, *, style: TextStyle | None = None) -> Bold:
    """Compatibility helper for bold inline text."""

    return Text.bold(value, style=style)


def italic(value: str, *, style: TextStyle | None = None) -> Italic:
    """Compatibility helper for italic inline text."""

    return Text.italic(value, style=style)


def code(value: str, *, style: TextStyle | None = None) -> Monospace:
    """Compatibility helper for monospace inline text."""

    return Text.code(value, style=style)


def _normalize_chip_kind(kind: str) -> str:
    normalized = kind.strip().lower().replace("_", "-")
    if not normalized or any(not (char.isalnum() or char == "-") for char in normalized):
        raise ValueError(f"Unsupported inline chip kind: {kind!r}")
    return normalized


def _default_chip_style(kind: str) -> InlineChipStyle:
    normalized = _normalize_chip_kind(kind)
    style = _DEFAULT_CHIP_STYLES.get(normalized, _DEFAULT_CHIP_STYLES["chip"])
    return style.merged()


def _default_status_chip_style(state: str) -> InlineChipStyle:
    normalized = state.strip().lower().replace("_", "-")
    style = _STATUS_CHIP_STYLES.get(normalized)
    if style is None:
        allowed = ", ".join(sorted(_STATUS_CHIP_STYLES))
        raise ValueError(f"Unsupported status state: {state!r}; expected one of {allowed}")
    return style.merged()


def _chip(
    value: object,
    *,
    kind: str,
    chip_style: InlineChipStyle | None = None,
    style: TextStyle | None = None,
    **style_values: object,
) -> InlineChip:
    resolved_style = chip_style or _default_chip_style(kind)
    if style_values:
        resolved_style = resolved_style.merged(**style_values)
    return InlineChip(value, chip_style=resolved_style, kind=kind, style=style)


def tag(
    value: object,
    *,
    chip_style: InlineChipStyle | None = None,
    style: TextStyle | None = None,
    **style_values: object,
) -> InlineChip:
    """Create a category or keyword chip."""

    return _chip(value, kind="tag", chip_style=chip_style, style=style, **style_values)


def badge(
    value: object,
    *,
    chip_style: InlineChipStyle | None = None,
    style: TextStyle | None = None,
    **style_values: object,
) -> InlineChip:
    """Create a count, label, or small emphasis chip."""

    return _chip(value, kind="badge", chip_style=chip_style, style=style, **style_values)


def status(
    value: object,
    *,
    state: str = "neutral",
    chip_style: InlineChipStyle | None = None,
    style: TextStyle | None = None,
    **style_values: object,
) -> InlineChip:
    """Create a state indicator chip."""

    resolved_style = chip_style or _default_status_chip_style(state)
    if style_values:
        resolved_style = resolved_style.merged(**style_values)
    return InlineChip(value, chip_style=resolved_style, kind="status", style=style)


def keyboard(
    value: object,
    *,
    chip_style: InlineChipStyle | None = None,
    style: TextStyle | None = None,
    **style_values: object,
) -> InlineChip:
    """Create a keyboard key chip."""

    return _chip(value, kind="keyboard", chip_style=chip_style, style=style, **style_values)


def color(
    value: str,
    color: str,
    *,
    style: TextStyle | None = None,
) -> Text:
    """Compatibility helper for colored inline text."""

    return Text.color(value, color, style=style)


def highlight(
    value: str,
    color: str = "FFFF00",
    *,
    style: TextStyle | None = None,
) -> Highlight:
    """Compatibility helper for highlighted inline text."""

    return Text.highlight(value, color=color, style=style)


def strike(value: str, *, style: TextStyle | None = None) -> Strikethrough:
    """Compatibility helper for strikethrough inline text."""

    return Text.strikethrough(value, style=style)


def strikethrough(value: str, *, style: TextStyle | None = None) -> Strikethrough:
    """Compatibility helper for strikethrough inline text."""

    return Text.strikethrough(value, style=style)


def line_break() -> LineBreak:
    """Create a manual line break inside a paragraph."""

    return LineBreak()


def link(
    target: str,
    *label: InlineInput,
    style: TextStyle | None = None,
) -> Hyperlink:
    """Compatibility helper for hyperlink creation."""

    return Hyperlink.external(target, *label, style=style)


InlineInput = Text | str | Sequence["InlineInput"] | None | object


def coerce_inlines(values: Iterable[InlineInput]) -> list[Text]:
    """Normalize supported inline inputs into ``Text`` fragments."""

    normalized: list[Text] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, Text):
            normalized.append(value)
            continue
        if _is_positioned_inline(value):
            normalized.append(value)  # type: ignore[arg-type]
            continue
        if _is_referenceable(value):
            raise TypeError(
                "Document objects must be cited explicitly with reference(obj) "
                "or obj.reference() before they are placed inside Paragraph(...)"
            )
        if isinstance(value, str):
            normalized.append(Text(value))
            continue
        if isinstance(value, Sequence):
            normalized.extend(coerce_inlines(value))
            continue
        raise TypeError(f"Unsupported inline value: {type(value)!r}")
    return normalized


def _is_referenceable(value: object) -> bool:
    block_name = type(value).__name__
    return block_name in {
        "Box",
        "Chapter",
        "CodeBlock",
        "Equation",
        "Figure",
        "Paragraph",
        "Part",
        "Section",
        "SubFigure",
        "SubFigureGroup",
        "Subsection",
        "Subsubsection",
        "Table",
    }


def _is_positioned_inline(value: object) -> bool:
    value_type = type(value)
    return (
        value_type.__module__ == "docscriptor.components.positioning"
        and value_type.__name__ in {"ImageBox", "Shape", "TextBox"}
    )


_BlockReference = BlockReference

__all__ = [
    "Bold",
    "Citation",
    "Comment",
    "Emphasis",
    "Footnote",
    "Highlight",
    "Hyperlink",
    "InlineChip",
    "InlineChipStyle",
    "Italic",
    "LineBreak",
    "Math",
    "Monospace",
    "Strong",
    "Strikethrough",
    "Text",
    "_BlockReference",
    "badge",
    "bold",
    "code",
    "color",
    "coerce_inlines",
    "cite",
    "comment",
    "footnote",
    "highlight",
    "italic",
    "keyboard",
    "link",
    "line_break",
    "math",
    "reference",
    "status",
    "strike",
    "strikethrough",
    "styled",
    "tag",
]
