"""Nodos mínimos y serializables del AST de InvestRule."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
import json
from typing import Any, Dict, Tuple, Union


class AstNode:
    """Comportamiento compartido por todos los nodos del AST."""

    def to_dict(self) -> Dict[str, Any]:
        return _to_serializable(self)

    def pretty(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass(frozen=True)
class Value(AstNode):
    kind: str
    value: Union[int, bool]


@dataclass(frozen=True)
class Comparison(AstNode):
    identifier: str
    operator: str
    value: Value


@dataclass(frozen=True)
class BinaryLogical(AstNode):
    operator: str
    left: "Expression"
    right: "Expression"


@dataclass(frozen=True)
class Not(AstNode):
    operand: "Expression"


Expression = Union[Comparison, BinaryLogical, Not]


@dataclass(frozen=True)
class Action(AstNode):
    kind: str
    target: str


@dataclass(frozen=True)
class Rule(AstNode):
    condition: Expression
    action: Action


@dataclass(frozen=True)
class Program(AstNode):
    rules: Tuple[Rule, ...]


def _to_serializable(value: Any) -> Any:
    if isinstance(value, AstNode) and is_dataclass(value):
        result = {"node": value.__class__.__name__}
        result.update(
            {
                field.name: _to_serializable(getattr(value, field.name))
                for field in fields(value)
            }
        )
        return result
    if isinstance(value, tuple):
        return [_to_serializable(item) for item in value]
    return value
