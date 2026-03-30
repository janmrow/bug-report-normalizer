from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bug-report-normalizer",
        description="Normalize raw bug notes into a structured draft bug report.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="bug-report-normalizer 0.1.0",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)

    print("Bootstrap complete. CLI workflow will be added in later commits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
