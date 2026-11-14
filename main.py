"""Interfaz de línea de comandos para analizar reglas InvestRule."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from src.errors import InvestRuleError
from src.parser import parse_text


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Valida un programa InvestRule e imprime su AST en JSON."
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "text",
        nargs="?",
        help="programa InvestRule; si se omite, se lee desde stdin",
    )
    source.add_argument(
        "-f",
        "--file",
        type=Path,
        help="archivo UTF-8 con reglas InvestRule",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_argument_parser().parse_args(argv)
    try:
        if args.file is not None:
            text = args.file.read_text(encoding="utf-8")
        elif args.text is not None:
            text = args.text
        else:
            text = sys.stdin.read()
        print(parse_text(text).pretty())
        return 0
    except (InvestRuleError, OSError, UnicodeError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
