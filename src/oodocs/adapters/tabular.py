"""Tabular adapters built on OODocs table helpers."""

from __future__ import annotations

from typing import Sequence

from oodocs.components.media import Table
from oodocs.core import PathLike


def table_from_records(records: Sequence[object], **kwargs: object) -> Table:
    """Return a ``Table`` from ordinary Python records."""

    return Table.from_records(records, **kwargs)


def table_from_csv(path: PathLike, **kwargs: object) -> Table:
    """Return a ``Table`` from a CSV file."""

    return Table.from_csv(path, **kwargs)


def table_from_tsv(path: PathLike, **kwargs: object) -> Table:
    """Return a ``Table`` from a TSV file."""

    return Table.from_tsv(path, **kwargs)


__all__ = ["table_from_csv", "table_from_records", "table_from_tsv"]
