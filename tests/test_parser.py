import unittest

from src.ast_nodes import BinaryLogical, Not
from src.errors import ParserError
from src.lexer import tokenize
from src.parser import parse_text, parse_tokens


class ParserValidInputTests(unittest.TestCase):
    def test_accepts_simple_rule(self):
        program = parse_text(
            "WHEN ganancias > 500000 THEN REINVERTIR ganancias;"
        )
        self.assertEqual(len(program.rules), 1)
        self.assertEqual(program.rules[0].action.kind, "REINVERTIR")

    def test_accepts_and_expression(self):
        program = parse_text(
            "WHEN retorno_esperado >= 12 AND riesgo <= 3 "
            "THEN APROBAR inversion;"
        )
        self.assertEqual(program.rules[0].condition.operator, "AND")

    def test_accepts_not_parentheses_and_or(self):
        program = parse_text(
            "WHEN NOT (riesgo > 3 OR perdida > 200000) "
            "AND ganancias >= 100000 THEN REINVERTIR ganancias;"
        )
        condition = program.rules[0].condition
        self.assertIsInstance(condition, BinaryLogical)
        self.assertIsInstance(condition.left, Not)
        self.assertEqual(condition.left.operand.operator, "OR")

    def test_accepts_two_consecutive_rules(self):
        program = parse_text(
            "WHEN ganancias > 500000 THEN REINVERTIR ganancias;\n"
            "WHEN riesgo > 4 THEN ALERTAR inversion;"
        )
        self.assertEqual(len(program.rules), 2)

    def test_accepts_boolean_and_zero_values(self):
        program = parse_text(
            "WHEN habilitada == TRUE OR perdidas == 0 THEN APROBAR proyecto;"
        )
        condition = program.rules[0].condition
        self.assertTrue(condition.left.value.value)
        self.assertEqual(condition.right.value.value, 0)

    def test_accepts_repeated_not_and_nested_parentheses(self):
        program = parse_text(
            "WHEN NOT NOT ((riesgo > 3)) THEN ALERTAR inversion;"
        )
        condition = program.rules[0].condition
        self.assertIsInstance(condition, Not)
        self.assertIsInstance(condition.operand, Not)

    def test_parse_tokens_is_primary_public_api(self):
        tokens = tokenize("WHEN a != FALSE THEN ALERTAR inversion;")
        program = parse_tokens(tokens)
        self.assertEqual(program.rules[0].condition.value.kind, "FALSE")

    def test_accepts_lowercase_keywords(self):
        program = parse_text("when a > 1 then alertar inversion;")
        self.assertEqual(program.rules[0].action.kind, "ALERTAR")


class ParserInvalidInputTests(unittest.TestCase):
    def test_rejects_empty_program(self):
        with self.assertRaisesRegex(ParserError, "programa no vacío"):
            parse_text("")

    def test_reports_omitted_value(self):
        with self.assertRaisesRegex(
            ParserError, "como valor de la comparación"
        ):
            parse_text("WHEN ganancias > THEN REINVERTIR ganancias;")

    def test_reports_omitted_then(self):
        with self.assertRaisesRegex(ParserError, "después de la condición"):
            parse_text("WHEN ganancias > 500000 REINVERTIR ganancias;")

    def test_reports_missing_action_identifier(self):
        with self.assertRaisesRegex(ParserError, "objetivo de la acción"):
            parse_text("WHEN ganancias > 500000 THEN REINVERTIR;")

    def test_reports_unclosed_parenthesis(self):
        with self.assertRaisesRegex(ParserError, "cerrar el paréntesis"):
            parse_text("WHEN (riesgo > 3 THEN ALERTAR inversion;")

    def test_reports_missing_operand_after_and(self):
        with self.assertRaises(ParserError) as caught:
            parse_text("WHEN a > 1 AND THEN ALERTAR inversion;")
        self.assertEqual(
            caught.exception.expected,
            ("NOT", "PARENT_IZQ", "ID"),
        )

    def test_reports_missing_semicolon(self):
        with self.assertRaisesRegex(ParserError, "al final de la regla"):
            parse_text("WHEN ganancias > 500000 THEN REINVERTIR ganancias")

    def test_rejects_trailing_tokens_after_valid_rule(self):
        with self.assertRaisesRegex(ParserError, "regla completa"):
            parse_text(
                "WHEN a > 1 THEN ALERTAR inversion; texto_sobrante"
            )


if __name__ == "__main__":
    unittest.main()
