"""Command line interface for OODocs workflows."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from oodocs.compatibility import normalize_output_formats
from oodocs.validation import DocumentValidationError
from oodocs.workflows import build_python_document, convert_source, validate_source


def main(argv: Sequence[str] | None = None) -> int:
    """Run the OODocs CLI."""

    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except DocumentValidationError as exc:
        print(exc, file=sys.stderr)
        return 1
    except (AttributeError, FileNotFoundError, ImportError, TypeError, ValueError) as exc:
        print(f"oodocs: {exc}", file=sys.stderr)
        return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oodocs",
        description="Build, convert, and validate OODocs documents.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser(
        "build",
        help="Build a Python-authored OODocs document.",
    )
    build.add_argument("source", help="Python file exposing a Document or build function.")
    _add_render_options(build, default_out=".")
    build.add_argument(
        "--factory",
        help="Document variable or zero-argument function to use from the Python source.",
    )
    build.add_argument(
        "--no-chdir",
        action="store_true",
        help="Do not run the Python source with its directory as the working directory.",
    )
    build.set_defaults(func=_run_build)

    convert = subparsers.add_parser(
        "convert",
        help="Convert Markdown or notebook source to rendered outputs.",
    )
    convert.add_argument("source", help="Markdown (.md) or notebook (.ipynb) file.")
    _add_render_options(convert, default_out=None)
    convert.add_argument("--title", help="Override the imported document title.")
    convert.set_defaults(func=_run_convert)

    validate = subparsers.add_parser(
        "validate",
        help="Validate a Python, Markdown, or notebook source document.",
    )
    validate.add_argument("source", help="Source file to validate.")
    validate.add_argument(
        "--to",
        default="docx,pdf,html",
        help="Comma-separated output formats to validate for. Defaults to docx,pdf,html.",
    )
    validate.add_argument(
        "--type",
        choices=("python", "py", "markdown", "md", "notebook", "ipynb"),
        help="Override source type inference.",
    )
    validate.add_argument("--title", help="Override imported Markdown/notebook title.")
    validate.add_argument(
        "--factory",
        help="Document variable or zero-argument function for Python sources.",
    )
    validate.add_argument(
        "--strict",
        action="store_true",
        help="Return a non-zero exit code when warnings are present.",
    )
    validate.add_argument(
        "--no-chdir",
        action="store_true",
        help="Do not run Python sources with their directory as the working directory.",
    )
    validate.set_defaults(func=_run_validate)

    return parser


def _add_render_options(
    parser: argparse.ArgumentParser,
    *,
    default_out: str | None,
) -> None:
    parser.add_argument(
        "--out",
        default=default_out,
        help=(
            "Output directory. Defaults to the current directory for build and "
            "the source directory for convert."
        ),
    )
    parser.add_argument(
        "--to",
        default="docx,pdf,html",
        help="Comma-separated output formats. Defaults to docx,pdf,html.",
    )
    parser.add_argument("--stem", help="Output filename stem.")
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation before rendering.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print slow major build steps.",
    )


def _run_build(args: argparse.Namespace) -> int:
    formats = _parse_formats(args.to)
    outputs = build_python_document(
        args.source,
        args.out,
        formats=formats,
        stem=args.stem,
        factory=args.factory,
        validate=not args.no_validate,
        chdir=not args.no_chdir,
        verbose=args.verbose,
    )
    _print_outputs(outputs.outputs)
    return 0


def _run_convert(args: argparse.Namespace) -> int:
    formats = _parse_formats(args.to)
    outputs = convert_source(
        args.source,
        args.out,
        formats=formats,
        stem=args.stem,
        title=args.title,
        validate=not args.no_validate,
        verbose=args.verbose,
    )
    _print_outputs(outputs.outputs)
    return 0


def _run_validate(args: argparse.Namespace) -> int:
    formats = _parse_formats(args.to)
    result = validate_source(
        args.source,
        source_type=args.type,
        title=args.title,
        factory=args.factory,
        formats=formats,
        chdir=not args.no_chdir,
    )
    print(result.format_table(formats=formats))
    if result.errors_for(formats):
        return 1
    if args.strict and result.warnings_for(formats):
        return 1
    return 0


def _parse_formats(value: str) -> tuple[str, ...]:
    pieces = tuple(piece.strip() for piece in value.split(",") if piece.strip())
    if not pieces:
        raise ValueError("--to must include at least one output format")
    return normalize_output_formats(pieces)


def _print_outputs(outputs: dict[object, Path]) -> None:
    for output_format, path in outputs.items():
        print(f"Wrote {output_format}: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
