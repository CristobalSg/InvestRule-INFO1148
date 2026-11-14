"""Excepciones localizadas para las etapas léxica y sintáctica."""

from __future__ import annotations

from typing import Iterable, Sequence


class InvestRuleError(Exception):
    """Clase base para los errores que se pueden mostrar al usuario."""


class LexicalError(InvestRuleError):
    """Indica que el lexer encontró un carácter fuera del lenguaje."""

    def __init__(
        self, character: str, index: int, line: int, column: int
    ) -> None:
        self.character = character
        self.index = index
        self.line = line
        self.column = column
        super().__init__(
            "Error léxico en línea "
            f"{line}, columna {column} (índice {index}): "
            f"símbolo no reconocido {character!r}."
        )


_EXPECTED_LABELS = {
    "WHEN": "'WHEN'",
    "THEN": "'THEN'",
    "AND": "'AND'",
    "OR": "'OR'",
    "NOT": "'NOT'",
    "REINVERTIR": "'REINVERTIR'",
    "APROBAR": "'APROBAR'",
    "ALERTAR": "'ALERTAR'",
    "TRUE": "'TRUE'",
    "FALSE": "'FALSE'",
    "ID": "un identificador (ID)",
    "NUM": "un entero no negativo (NUM)",
    "OP_REL": "un comparador (>=, <=, ==, !=, > o <)",
    "PUNTO_COMA": "';'",
    "PARENT_IZQ": "'('",
    "PARENT_DER": "')'",
    "EOF": "el fin de la entrada",
}


def _join_expected(expected: Sequence[str]) -> str:
    labels = [
        _EXPECTED_LABELS.get(token_type, token_type)
        for token_type in expected
    ]
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + " o " + labels[-1]


class ParserError(InvestRuleError):
    """Indica que el flujo de tokens no cumple la GLC de InvestRule."""

    def __init__(
        self,
        expected: Iterable[str],
        found: object,
        context: str | None = None,
    ) -> None:
        ordered_expected = tuple(dict.fromkeys(expected))
        self.expected = ordered_expected
        self.found = found
        self.context = context

        token_type = getattr(found, "type")
        lexeme = getattr(found, "lexeme")
        line = getattr(found, "line")
        column = getattr(found, "column")
        index = getattr(found, "index")

        found_description = (
            "el fin de la entrada"
            if token_type == "EOF"
            else f"{token_type} ({lexeme!r})"
        )
        context_text = f" {context}" if context else ""
        super().__init__(
            "Error sintáctico en línea "
            f"{line}, columna {column} (índice {index}): "
            f"se esperaba {_join_expected(ordered_expected)}{context_text}; "
            f"se encontró {found_description}."
        )
