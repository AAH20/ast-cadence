"""
Data models and contract specifications for AST-Cadence.
Static Call-Graph AST Slicer & Semantic Topology Compactor for Coding Agent Contexts.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set
import time


class SymbolType(str, Enum):
    FUNCTION = "FUNCTION"
    METHOD = "METHOD"
    CLASS = "CLASS"
    INTERFACE = "INTERFACE"


@dataclass
class ExtractedSymbol:
    name: str
    symbol_type: SymbolType
    parent_class: Optional[str] = None
    signature: str = ""
    calls: List[str] = field(default_factory=list)
    line_number: int = 0
    is_exported: bool = True


@dataclass
class SkeletalContract:
    target_symbol: str
    distilled_code: str
    original_token_count: int
    compacted_token_count: int
    compression_ratio: float
    referenced_symbols: List[str] = field(default_factory=list)
    latency_ms: float = 0.0


@dataclass
class CadenceMetrics:
    files_analyzed: int = 0
    symbols_indexed: int = 0
    tokens_saved: int = 0
    avg_compression_ratio: float = 0.0
