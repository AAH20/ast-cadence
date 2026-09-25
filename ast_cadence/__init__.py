"""
ast-cadence: Static Call-Graph AST Slicer & Semantic Topology Compactor for Coding Agent Contexts.
"""

from .models import (
    SymbolType,
    ExtractedSymbol,
    SkeletalContract,
    CadenceMetrics,
)
from .ast_analyzer import ASTAnalyzer
from .slicer import CallGraphSlicer

__version__ = "0.1.0"
__all__ = [
    "SymbolType",
    "ExtractedSymbol",
    "SkeletalContract",
    "CadenceMetrics",
    "ASTAnalyzer",
    "CallGraphSlicer",
]
