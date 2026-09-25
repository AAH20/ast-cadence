"""
Static AST Analyzer & Symbol Extractor for AST-Cadence.
"""

import ast
from typing import Dict, List, Optional
from .models import SymbolType, ExtractedSymbol


class SymbolVisitor(ast.NodeVisitor):
    """Walks Python AST extracting typed symbol signatures and call references."""

    def __init__(self):
        self.symbols: List[ExtractedSymbol] = []
        self._current_class: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef):
        bases = [ast.unparse(b) for b in node.bases]
        sig = f"class {node.name}" + (f"({', '.join(bases)})" if bases else "") + ":"
        self.symbols.append(ExtractedSymbol(
            name=node.name,
            symbol_type=SymbolType.CLASS,
            signature=sig,
            line_number=node.lineno,
            is_exported=not node.name.startswith("_")
        ))

        old_class = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._record_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._record_func(node, is_async=True)

    def _record_func(self, node, is_async: bool = False):
        prefix = "async def " if is_async else "def "
        args = ast.unparse(node.args)
        ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
        sig = f"{prefix}{node.name}({args}){ret}:"

        calls = []
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name):
                    calls.append(n.func.id)
                elif isinstance(n.func, ast.Attribute):
                    calls.append(n.func.attr)

        stype = SymbolType.METHOD if self._current_class else SymbolType.FUNCTION

        self.symbols.append(ExtractedSymbol(
            name=node.name,
            symbol_type=stype,
            parent_class=self._current_class,
            signature=sig,
            calls=list(set(calls)),
            line_number=node.lineno,
            is_exported=not node.name.startswith("_")
        ))
        self.generic_visit(node)


class ASTAnalyzer:
    """Parses Python source files into indexed symbol metadata."""

    @staticmethod
    def parse_code(code_str: str) -> List[ExtractedSymbol]:
        tree = ast.parse(code_str)
        visitor = SymbolVisitor()
        visitor.visit(tree)
        return visitor.symbols
