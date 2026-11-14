"""Parser predictivo LL(1) propio, implementado por descenso recursivo."""

from __future__ import annotations

from typing import List, Sequence

from .ast_nodes import (
    Action,
    BinaryLogical,
    Comparison,
    Expression,
    Not,
    Program,
    Rule,
    Value,
)
from .errors import ParserError
from .lexer import Token, _advance_position, tokenize


_EXPRESSION_START = ("NOT", "PARENT_IZQ", "ID")
_OR_FOLLOW = ("THEN", "PARENT_DER")
_AND_FOLLOW = ("OR", "THEN", "PARENT_DER")
_ACTION_START = ("REINVERTIR", "APROBAR", "ALERTAR")
_VALUE_START = ("NUM", "TRUE", "FALSE")


class Parser:
    """Consume tokens según las producciones congeladas P01-P21."""

    def __init__(self, tokens: Sequence[Token]) -> None:
        supplied_tokens = list(tokens)
        if not all(isinstance(token, Token) for token in supplied_tokens):
            raise TypeError("parse_tokens espera una secuencia de objetos Token")
        if any(token.type == "EOF" for token in supplied_tokens):
            raise ValueError("EOF es interno al parser y no debe suministrarse")

        self._tokens: List[Token] = supplied_tokens + [
            self._make_eof(supplied_tokens)
        ]
        self._position = 0

    @staticmethod
    def _make_eof(tokens: Sequence[Token]) -> Token:
        if not tokens:
            return Token("EOF", "", 0, 1, 1)
        last = tokens[-1]
        line, column = _advance_position(last.lexeme, last.line, last.column)
        return Token(
            "EOF",
            "",
            last.index + len(last.lexeme),
            line,
            column,
        )

    @property
    def _current(self) -> Token:
        return self._tokens[self._position]

    def _accept(self, token_type: str) -> Token | None:
        if self._current.type != token_type:
            return None
        token = self._current
        self._position += 1
        return token

    def _expect(self, token_type: str, context: str | None = None) -> Token:
        token = self._accept(token_type)
        if token is None:
            raise ParserError((token_type,), self._current, context)
        return token

    def parse(self) -> Program:
        program = self._programa()
        self._expect("EOF")
        return program

    def _programa(self) -> Program:
        """P01: programa -> regla resto_programa."""

        if self._current.type != "WHEN":
            raise ParserError(
                ("WHEN",),
                self._current,
                "para iniciar un programa no vacío",
            )
        first_rule = self._regla()
        remaining_rules = self._resto_programa()
        return Program((first_rule, *remaining_rules))

    def _resto_programa(self) -> List[Rule]:
        """P02-P03: otra regla si hay WHEN; epsilon si hay EOF."""

        if self._current.type == "WHEN":
            rule = self._regla()
            return [rule, *self._resto_programa()]
        if self._current.type == "EOF":
            return []
        raise ParserError(
            ("WHEN", "EOF"),
            self._current,
            "después de una regla completa",
        )

    def _regla(self) -> Rule:
        """P04: regla -> WHEN expresion THEN accion PUNTO_COMA."""

        self._expect("WHEN")
        condition = self._expresion()
        self._expect("THEN", "después de la condición")
        action = self._accion()
        self._expect("PUNTO_COMA", "al final de la regla")
        return Rule(condition, action)

    def _expresion(self) -> Expression:
        """P05: expresion -> conjuncion cola_or."""

        if self._current.type not in _EXPRESSION_START:
            raise ParserError(_EXPRESSION_START, self._current)
        left = self._conjuncion()
        return self._cola_or(left)

    def _cola_or(self, left: Expression) -> Expression:
        """P06-P07: consume OR conjuncion repetidamente o epsilon."""

        if self._accept("OR"):
            right = self._conjuncion()
            return self._cola_or(BinaryLogical("OR", left, right))
        if self._current.type in _OR_FOLLOW:
            return left
        raise ParserError(("OR", *_OR_FOLLOW), self._current)

    def _conjuncion(self) -> Expression:
        """P08: conjuncion -> negacion cola_and."""

        left = self._negacion()
        return self._cola_and(left)

    def _cola_and(self, left: Expression) -> Expression:
        """P09-P10: consume AND negacion repetidamente o epsilon."""

        if self._accept("AND"):
            right = self._negacion()
            return self._cola_and(BinaryLogical("AND", left, right))
        if self._current.type in _AND_FOLLOW:
            return left
        if self._current.type in _ACTION_START:
            raise ParserError(
                ("THEN",),
                self._current,
                "después de la condición",
            )
        raise ParserError(("AND", *_AND_FOLLOW), self._current)

    def _negacion(self) -> Expression:
        """P11-P12: NOT negacion o primario."""

        if self._accept("NOT"):
            return Not(self._negacion())
        if self._current.type not in ("PARENT_IZQ", "ID"):
            raise ParserError(_EXPRESSION_START, self._current)
        return self._primario()

    def _primario(self) -> Expression:
        """P13-P14: expresión entre paréntesis o comparación."""

        if self._accept("PARENT_IZQ"):
            expression = self._expresion()
            self._expect(
                "PARENT_DER", "para cerrar el paréntesis abierto"
            )
            return expression
        if self._current.type == "ID":
            return self._comparacion()
        raise ParserError(("PARENT_IZQ", "ID"), self._current)

    def _comparacion(self) -> Comparison:
        """P15: comparacion -> ID OP_REL valor."""

        identifier = self._expect("ID")
        operator = self._expect("OP_REL", "después del identificador")
        value = self._valor()
        return Comparison(identifier.lexeme, operator.lexeme, value)

    def _valor(self) -> Value:
        """P16-P18: valor -> NUM | TRUE | FALSE."""

        if self._current.type == "NUM":
            token = self._expect("NUM")
            return Value("NUM", int(token.lexeme))
        if self._current.type == "TRUE":
            self._expect("TRUE")
            return Value("TRUE", True)
        if self._current.type == "FALSE":
            self._expect("FALSE")
            return Value("FALSE", False)
        raise ParserError(
            _VALUE_START,
            self._current,
            "como valor de la comparación",
        )

    def _accion(self) -> Action:
        """P19-P21: cada acción reservada seguida por un ID."""

        if self._current.type not in _ACTION_START:
            raise ParserError(
                _ACTION_START,
                self._current,
                "después de 'THEN'",
            )
        action = self._current
        self._position += 1
        target = self._expect("ID", "como objetivo de la acción")
        return Action(action.type, target.lexeme)


def parse_tokens(tokens: Sequence[Token]) -> Program:
    """Valida una secuencia de tokens y devuelve su AST."""

    return Parser(tokens).parse()


def parse_text(text: str) -> Program:
    """Atajo: tokeniza texto y analiza el flujo resultante."""

    return parse_tokens(tokenize(text))
