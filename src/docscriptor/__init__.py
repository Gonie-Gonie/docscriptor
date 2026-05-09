"""Top-level package for docscriptor."""

from importlib.metadata import PackageNotFoundError, version as package_version

from docscriptor.core import DocscriptorError
from docscriptor.components.blocks import (
    Box,
    BulletList,
    Chapter,
    CodeBlock,
    Equation,
    NumberedList,
    PageBreak,
    PageBreaker,
    Paragraph,
    Section,
    Subsection,
    Subsubsection,
)
from docscriptor.components.generated import CommentsPage, FigureList, ReferencesPage, TableList, TableOfContents, TocLevelStyle
from docscriptor.components.media import Figure, Table, TableCell
from docscriptor.components.markup import md, markup
from docscriptor.components.people import Affiliation, Author, AuthorLayout
from docscriptor.components.references import CitationLibrary, CitationSource
from docscriptor.components.positioning import ImageBox, Shape, TextBox
from docscriptor.document import Document
from docscriptor.components.inline import (
    Comment,
    Footnote,
    LineBreak,
    Math,
    Text,
    bold,
    code,
    color,
    cite,
    comment,
    footnote,
    highlight,
    italic,
    link,
    line_break,
    math,
    strike,
    strikethrough,
    styled,
)
from docscriptor.settings import (
    BoxStyle,
    DocumentSettings,
    HeadingNumbering,
    ListStyle,
    PageMargins,
    PageSize,
    ParagraphStyle,
    TableStyle,
    TextStyle,
    Theme,
)


def _resolve_version() -> str:
    try:
        return package_version("docscriptor")
    except PackageNotFoundError:
        try:
            from setuptools_scm import get_version
        except ImportError:
            return "0.7.0"
        return get_version(
            root="../..",
            relative_to=__file__,
            fallback_version="0.7.0",
            tag_regex=r"^v(?P<version>\d+\.\d+\.\d+)$",
        )


__version__ = _resolve_version()

__all__ = [
    "Affiliation",
    "Author",
    "AuthorLayout",
    "Box",
    "BoxStyle",
    "BulletList",
    "CitationLibrary",
    "CitationSource",
    "Chapter",
    "Comment",
    "CommentsPage",
    "CodeBlock",
    "Document",
    "DocumentSettings",
    "DocscriptorError",
    "Equation",
    "Figure",
    "FigureList",
    "Footnote",
    "HeadingNumbering",
    "ImageBox",
    "LineBreak",
    "ListStyle",
    "Math",
    "NumberedList",
    "PageMargins",
    "PageSize",
    "PageBreak",
    "PageBreaker",
    "Paragraph",
    "ParagraphStyle",
    "ReferencesPage",
    "Section",
    "Shape",
    "Subsection",
    "Subsubsection",
    "Table",
    "TableCell",
    "TableStyle",
    "TableOfContents",
    "TableList",
    "Text",
    "TextBox",
    "TextStyle",
    "Theme",
    "TocLevelStyle",
    "__version__",
    "bold",
    "code",
    "color",
    "cite",
    "comment",
    "footnote",
    "highlight",
    "italic",
    "link",
    "line_break",
    "math",
    "strike",
    "strikethrough",
    "md",
    "markup",
    "styled",
]

for _module_name in ("components", "core", "document", "layout", "settings"):
    globals().pop(_module_name, None)

del _resolve_version
del _module_name
