import unittest

from src.ast_nodes import BinaryLogical, Comparison, Not
from src.parser import parse_text


class AstTests(unittest.TestCase):
    def test_and_has_higher_precedence_than_or(self):
        program = parse_text(
            "WHEN a > 1 OR b < 2 AND c == 3 THEN ALERTAR inversion;"
        )
        condition = program.rules[0].condition
        self.assertIsInstance(condition, BinaryLogical)
        self.assertEqual(condition.operator, "OR")
        self.assertIsInstance(condition.left, Comparison)
        self.assertIsInstance(condition.right, BinaryLogical)
        self.assertEqual(condition.right.operator, "AND")

    def test_parentheses_override_default_precedence(self):
        program = parse_text(
            "WHEN (a > 1 OR b < 2) AND c == 3 THEN APROBAR inversion;"
        )
        condition = program.rules[0].condition
        self.assertEqual(condition.operator, "AND")
        self.assertEqual(condition.left.operator, "OR")

    def test_not_wraps_complete_parenthesized_disjunction(self):
        program = parse_text(
            "WHEN NOT (a > 1 OR b < 2) THEN ALERTAR inversion;"
        )
        condition = program.rules[0].condition
        self.assertIsInstance(condition, Not)
        self.assertEqual(condition.operand.operator, "OR")

    def test_ast_serialization_is_readable_and_json_compatible(self):
        program = parse_text("WHEN a > 1 THEN ALERTAR inversion;")
        serialized = program.to_dict()
        self.assertEqual(serialized["node"], "Program")
        self.assertEqual(
            serialized["rules"][0]["condition"]["node"], "Comparison"
        )
        self.assertIn('"node": "Program"', program.pretty())


if __name__ == "__main__":
    unittest.main()
