"""Adapters for JSON release or reproducibility manifests."""

from __future__ import annotations

import json
from pathlib import Path

from oodocs.components.blocks import Paragraph, Section
from oodocs.components.inline import code
from oodocs.components.media import Table
from oodocs.core import PathLike
from oodocs.layout.theme import TableStyle


def section_from_manifest(path: PathLike) -> Section:
    """Create a section from a JSON manifest file."""

    source_path = Path(path)
    data = json.loads(source_path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        table = Table.from_mapping(
            data,
            caption=f"Manifest values from {source_path.name}.",
            style=TableStyle.evidence(),
        )
    elif isinstance(data, list):
        table = Table.from_records(
            data,
            caption=f"Manifest rows from {source_path.name}.",
            style=TableStyle.evidence(),
        )
    else:
        table = Table(
            ["Value"],
            [[json.dumps(data, ensure_ascii=False)]],
            caption=f"Manifest value from {source_path.name}.",
            style=TableStyle.evidence(),
        )
    return Section(
        "Reproducibility manifest",
        Paragraph("Read from ", code(source_path.as_posix()), "."),
        table,
        numbered=False,
        toc=True,
    )


__all__ = ["section_from_manifest"]
