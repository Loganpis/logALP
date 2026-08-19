"""Command-line entry point for the logALP pre-alpha scaffold."""

from __future__ import annotations

import argparse

from logalp import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logalp",
        description=(
            "logALP magnetic-field morphology benchmarks "
            "(pre-alpha specification release)"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"logALP {__version__}",
    )
    return parser


def main() -> int:
    """Run the currently available pre-alpha command-line interface."""
    build_parser().parse_args()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
