"""
Call-Graph Dependency Slicer & Skeletal Topology Compactor for AST-Cadence.
"""

import time
from typing import Dict, List, Set, Optional
from .models import SymbolType, ExtractedSymbol, SkeletalContract, CadenceMetrics
from .ast_analyzer import ASTAnalyzer


class CallGraphSlicer:
    """Extracts semantic dependency slices and condenses full codebases into skeletal contracts."""

    def __init__(self):
        self.metrics = CadenceMetrics()

    def condense_repo_for_target(
        self,
        files: Dict[str, str],
        target_symbol_name: str
    ) -> SkeletalContract:
        """
        Parses all files, builds dependency graph from target_symbol_name,
        and assembles a compacted skeletal contract for LLM ingestion.
        """
        start_time = time.time()
        all_symbols: Dict[str, ExtractedSymbol] = {}
        total_raw_chars = 0

        # 1. Parse AST of all files
        for filename, code in files.items():
            total_raw_chars += len(code)
            self.metrics.files_analyzed += 1
            file_symbols = ASTAnalyzer.parse_code(code)
            for sym in file_symbols:
                all_symbols[sym.name] = sym
                self.metrics.symbols_indexed += 1

        # 2. Build Dependency Cone (Breadth-First Search)
        needed_symbols: Set[str] = set()
        queue = [target_symbol_name]

        while queue:
            curr = queue.pop(0)
            if curr in needed_symbols or curr not in all_symbols:
                continue

            needed_symbols.add(curr)
            sym = all_symbols[curr]

            # If method, add its parent class
            if sym.parent_class and sym.parent_class in all_symbols:
                needed_symbols.add(sym.parent_class)

            # Traverse callee references
            for callee in sym.calls:
                if callee in all_symbols and callee not in needed_symbols:
                    queue.append(callee)

        # 3. Assemble Distilled Skeletal Topology
        lines = [
            f"# AST-CADENCE DISTILLED SKELETAL TOPOLOGY",
            f"# Target Focus: {target_symbol_name}",
            f"# Dependency Slice: {len(needed_symbols)} symbols referenced\n"
        ]

        # Group by classes
        classes_rendered: Set[str] = set()
        for sym_name in sorted(needed_symbols):
            sym = all_symbols[sym_name]
            if sym.symbol_type == SymbolType.CLASS:
                lines.append(f"{sym.signature}")
                classes_rendered.add(sym.name)
                # Find methods of this class
                for child_name in sorted(needed_symbols):
                    child = all_symbols[child_name]
                    if child.parent_class == sym.name:
                        lines.append(f"    {child.signature}")
                        lines.append(f"        ...\n")
                lines.append("")
            elif sym.symbol_type == SymbolType.FUNCTION and not sym.parent_class:
                lines.append(f"{sym.signature}")
                lines.append(f"    ...\n")

        distilled_code = "\n".join(lines)
        compacted_chars = len(distilled_code)

        # Token estimates (~4 chars per token)
        raw_tokens = max(1, total_raw_chars // 4)
        compacted_tokens = max(1, compacted_chars // 4)
        compression_ratio = round(1.0 - (compacted_tokens / raw_tokens), 3)

        self.metrics.tokens_saved += max(0, raw_tokens - compacted_tokens)
        duration_ms = (time.time() - start_time) * 1000.0

        return SkeletalContract(
            target_symbol=target_symbol_name,
            distilled_code=distilled_code,
            original_token_count=raw_tokens,
            compacted_token_count=compacted_tokens,
            compression_ratio=compression_ratio,
            referenced_symbols=sorted(list(needed_symbols)),
            latency_ms=duration_ms
        )
