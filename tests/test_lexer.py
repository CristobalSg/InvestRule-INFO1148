import unittest

from src.errors import LexicalError
from src.lexer import analizador_lexico, tokenize


class LexerTests(unittest.TestCase):
    def test_recognizes_complete_simple_rule(self):
        tokens = tokenize(
            "WHEN ganancias >= 500000 THEN REINVERTIR ganancias;"
        )
        self.assertEqual(
            [token.type for token in tokens],
            [
                "WHEN",
                "ID",
                "OP_REL",
                "NUM",
                "THEN",
                "REINVERTIR",
                "ID",
                "PUNTO_COMA",
            ],
        )

    def test_reserved_words_are_case_insensitive_and_keep_lexeme(self):
        tokens = tokenize("when True then aprobar proyecto;")
        self.assertEqual(tokens[0].type, "WHEN")
        self.assertEqual(tokens[0].lexeme, "when")
        self.assertEqual(tokens[1].type, "TRUE")
        self.assertEqual(tokens[3].type, "APROBAR")

    def test_all_actions_and_boolean_are_reserved(self):
        tokens = tokenize("REINVERTIR aprobar ALERTAR FALSE")
        self.assertEqual(
            [token.type for token in tokens],
            ["REINVERTIR", "APROBAR", "ALERTAR", "FALSE"],
        )

    def test_positions_include_line_column_and_index(self):
        tokens = tokenize("WHEN a > 1\nTHEN ALERTAR x;")
        then = tokens[4]
        self.assertEqual((then.index, then.line, then.column), (11, 2, 1))

    def test_unknown_character_raises_localized_lexical_error(self):
        with self.assertRaises(LexicalError) as caught:
            tokenize("WHEN a $ 1")
        error = caught.exception
        self.assertEqual((error.character, error.index), ("$", 7))
        self.assertIn("línea 1, columna 8", str(error))

    def test_decimal_is_not_accepted(self):
        with self.assertRaisesRegex(LexicalError, r"símbolo no reconocido '\.'"):
            tokenize("WHEN tasa > 12.5 THEN APROBAR inversion;")

    def test_negative_number_is_not_accepted(self):
        with self.assertRaisesRegex(LexicalError, "símbolo no reconocido '-'"):
            tokenize("WHEN saldo > -1 THEN ALERTAR inversion;")

    def test_notebook_compatibility_function_returns_pairs(self):
        self.assertEqual(
            analizador_lexico("NOT riesgo <= 3"),
            [("NOT", "NOT"), ("ID", "riesgo"), ("OP_REL", "<="), ("NUM", "3")],
        )


if __name__ == "__main__":
    unittest.main()
