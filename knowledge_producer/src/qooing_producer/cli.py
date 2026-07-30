from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from .bundle import generate_indexes, validate_bundle


def parser() -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(prog="qooing-kb")
    subcommands = command_parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "index"):
        command = subcommands.add_parser(name)
        command.add_argument("bundle", type=Path)
    return command_parser


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "index":
        generate_indexes(args.bundle)
    violations = validate_bundle(args.bundle)
    for violation in violations:
        print(violation)
    return 1 if violations else 0
