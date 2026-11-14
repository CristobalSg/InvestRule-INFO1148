"""Analizador léxico de InvestRule, adaptado del notebook de referencia."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import List, Tuple

from .errors import LexicalError


@dataclass(frozen=True)
class Token:
    """Token con lexema original y posición inicial en el texto."""

    type: str
    lexeme: str
    index: int
    line: int
    column: int

    @property
    def tipo(self) -> str:
        """Alias en español para facilitar la exposición del proyecto."""

        return self.type

    @property
    def lexema(self) -> str:
        return self.lexeme


_TOKEN_SPECIFICATION = (
    ("NUM", r"[0-9]+"),
    ("OP_REL", r">=|<=|==|!=|>|<"),
    ("PUNTO_COMA", r";"),
    ("PARENT_IZQ", r"\("),
    ("PARENT_DER", r"\)"),
    ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("ESPACIO", r"[ \t\r\n]+"),
    ("ERROR", r"."),
)

_TOKEN_PATTERN = re.compile(
    "|".join(
        f"(?P<{name}>{expression})"
        for name, expression in _TOKEN_SPECIFICATION
    )
)

_RESERVED_WORDS = {
    "WHEN",
    "THEN",
    "AND",
    "OR",
    "NOT",
    "REINVERTIR",
    "APROBAR",
    "ALERTAR",
    "TRUE",
    "FALSE",
}


def _advance_position(text: str, line: int, column: int) -> Tuple[int, int]:
    """Calcula la posición siguiente, aceptando LF, CRLF y CR."""

    previous_was_cr = False
    for character in text:
        if character == "\n":
            if not previous_was_cr:
                line += 1
            column = 1
            previous_was_cr = False
        elif character == "\r":
            line += 1
            column = 1
            previous_was_cr = True
        else:
            column += 1
            previous_was_cr = False
    return line, column


def tokenize(text: str) -> List[Token]:
    """Convierte texto en tokens de InvestRule y localiza errores léxicos."""

    tokens: List[Token] = []
    line = 1
    column = 1

    for match in _TOKEN_PATTERN.finditer(text):
        token_type = match.lastgroup
        lexeme = match.group()
        index = match.start()
        token_line = line
        token_column = column

        if token_type == "ERROR":
            raise LexicalError(lexeme, index, token_line, token_column)

        if token_type != "ESPACIO":
            if token_type == "ID" and lexeme.upper() in _RESERVED_WORDS:
                token_type = lexeme.upper()
            tokens.append(
                Token(token_type, lexeme, index, token_line, token_column)
            )

        line, column = _advance_position(lexeme, line, column)

    return tokens


def analizador_lexico(text: str) -> List[Tuple[str, str]]:
    """API compatible con el notebook: retorna pares ``(tipo, lexema)``."""

    return [(token.type, token.lexeme) for token in tokenize(text)]
