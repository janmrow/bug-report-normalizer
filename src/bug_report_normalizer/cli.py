from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import TextIO

from bug_report_normalizer.exceptions import BugReportDraftingError, LLMClientError
from bug_report_normalizer.llm_client import OllamaClient
from bug_report_normalizer.renderer import (
    render_bug_report_as_json,
    render_bug_report_as_text,
)
from bug_report_normalizer.service import draft_bug_report

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


class CLIUsageError(Exception):
    """Raised when the CLI input is missing or invalid."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bug-report-normalizer",
        description="Normalize raw bug notes into a structured draft bug report.",
    )

    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--note",
        help="Raw bug note passed directly on the command line.",
    )
    input_group.add_argument(
        "--input-file",
        help="Path to a UTF-8 text file containing the raw bug note.",
    )

    parser.add_argument(
        "--output-format",
        choices=("json", "text"),
        default="json",
        help="Output format for the normalized bug report.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OLLAMA_MODEL"),
        help="Ollama model name. Can also be provided via OLLAMA_MODEL.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL),
        help="Ollama base URL. Can also be provided via OLLAMA_BASE_URL.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="bug-report-normalizer 0.1.0",
    )

    return parser


def main(argv: list[str] | None = None, stdin: TextIO | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    stdin = stdin or sys.stdin

    try:
        if not args.model:
            raise CLIUsageError("Provide the Ollama model with --model or OLLAMA_MODEL.")

        raw_note = read_raw_note(args, stdin=stdin)

        client = OllamaClient(
            model=args.model,
            base_url=args.base_url,
        )

        draft = draft_bug_report(
            raw_note=raw_note,
            client=client,
        )

        if args.output_format == "json":
            output = render_bug_report_as_json(draft)
        else:
            output = render_bug_report_as_text(draft)

    except (CLIUsageError, OSError, ValueError, LLMClientError, BugReportDraftingError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(output)
    return 0


def read_raw_note(args: argparse.Namespace, *, stdin: TextIO) -> str:
    if args.note is not None:
        return _normalize_raw_note(args.note)

    if args.input_file is not None:
        file_content = Path(args.input_file).read_text(encoding="utf-8")
        return _normalize_raw_note(file_content)

    if _stdin_has_data(stdin):
        return _normalize_raw_note(stdin.read())

    raise CLIUsageError("Provide input with --note, --input-file, or stdin.")


def _normalize_raw_note(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise CLIUsageError("Bug note input must not be empty.")
    return normalized


def _stdin_has_data(stdin: TextIO) -> bool:
    isatty = getattr(stdin, "isatty", None)
    if callable(isatty):
        return not isatty()
    return True


if __name__ == "__main__":
    raise SystemExit(main())
