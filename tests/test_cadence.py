"""
Unit tests for AST-Cadence AST analysis, call graph slicing, and skeletal compaction.
"""

import unittest
from ast_cadence.models import SymbolType
from ast_cadence.ast_analyzer import ASTAnalyzer
from ast_cadence.slicer import CallGraphSlicer


class TestASTCadence(unittest.TestCase):

    def test_ast_analyzer_extraction(self):
        code = """
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

def standalone(x: str) -> None:
    pass
"""
        symbols = ASTAnalyzer.parse_code(code)
        sym_names = [s.name for s in symbols]
        self.assertIn("Calculator", sym_names)
        self.assertIn("add", sym_names)
        self.assertIn("standalone", sym_names)

        calc_class = [s for s in symbols if s.name == "Calculator"][0]
        self.assertEqual(calc_class.symbol_type, SymbolType.CLASS)

        add_method = [s for s in symbols if s.name == "add"][0]
        self.assertEqual(add_method.symbol_type, SymbolType.METHOD)
        self.assertEqual(add_method.parent_class, "Calculator")

    def test_call_graph_slicing_cone(self):
        files = {
            "a.py": """
def helper_callee(v: int) -> int:
    return v * 2

def target_func(num: int) -> int:
    return helper_callee(num)

def dead_uncalled_code():
    pass
"""
        }
        slicer = CallGraphSlicer()
        contract = slicer.condense_repo_for_target(files, "target_func")

        self.assertIn("target_func", contract.referenced_symbols)
        self.assertIn("helper_callee", contract.referenced_symbols)
        # Verify dead code was excluded
        self.assertNotIn("dead_uncalled_code", contract.referenced_symbols)
        self.assertIn("target_func", contract.distilled_code)
        self.assertNotIn("dead_uncalled_code", contract.distilled_code)

    def test_compression_ratio(self):
        files = {
            "service.py": """
class HeavyService:
    def target(self) -> None:
        self.sub_step()

    def sub_step(self) -> None:
        pass

    def huge_unrelated_method(self) -> None:
        # lots of lines
        x = 1
        y = 2
        z = x + y
"""
        }
        slicer = CallGraphSlicer()
        contract = slicer.condense_repo_for_target(files, "target")
        self.assertGreater(contract.compression_ratio, 0.0)
        self.assertLess(contract.compacted_token_count, contract.original_token_count)


if __name__ == "__main__":
    unittest.main()
