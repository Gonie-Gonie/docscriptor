"""Adapters that turn repository artefacts into OODocs objects."""

from oodocs.adapters.evidence import build_release_evidence_document, build_release_evidence_bundle
from oodocs.adapters.github_actions import section_from_github_workflow
from oodocs.adapters.manifest import section_from_manifest
from oodocs.adapters.pyproject import section_from_pyproject
from oodocs.adapters.tabular import table_from_csv, table_from_records, table_from_tsv

__all__ = [
    "build_release_evidence_bundle",
    "build_release_evidence_document",
    "section_from_github_workflow",
    "section_from_manifest",
    "section_from_pyproject",
    "table_from_csv",
    "table_from_records",
    "table_from_tsv",
]
