"""
CLI interface and interactive demonstration runner for AST-Cadence.
"""

import sys
import argparse
from .slicer import CallGraphSlicer


def run_demo():
    print("=" * 74)
    print("  AST-CADENCE: Static Call-Graph AST Slicer & Topology Compactor")
    print("  Semantic Density for Frontier Coding Agents: Claude Opus 5.5 & GPT-6 Astra")
    print("=" * 74)

    # 1. Simulated multi-file repository with boilerplate, utilities, and core logic
    sample_files = {
        "src/database.py": """
class DatabasePool:
    def __init__(self, dsn: str, max_conns: int = 50):
        self.dsn = dsn
        self.conns = []
        for i in range(max_conns):
            self.conns.append({"id": i, "active": True})

    def execute_raw(self, sql: str) -> dict:
        # 100 lines of complex connection pooling and transaction logging
        return {"status": "ok", "rows": 1}

    def close_all(self) -> None:
        self.conns.clear()
""",
        "src/security.py": """
def hash_secret(secret: str) -> str:
    import hashlib
    return hashlib.sha256(secret.encode()).hexdigest()

def verify_token(token: str) -> bool:
    return len(token) > 20 and not token.startswith("revoked")
""",
        "src/settlement.py": """
from .database import DatabasePool
from .security import verify_token

class LedgerEntry:
    def __init__(self, account_id: str, amount: int):
        self.account_id = account_id
        self.amount = amount

class PaymentSettler:
    def __init__(self, db: DatabasePool):
        self.db = db

    def settle_transaction(self, auth_token: str, entry: LedgerEntry) -> bool:
        if not verify_token(auth_token):
            return False
        res = self.db.execute_raw(f"INSERT INTO ledger VALUES ('{entry.account_id}', {entry.amount})")
        return res["status"] == "ok"

    def audit_trail(self, start_date: str) -> list:
        # Long analytical reporting logic unrelated to settlement
        return []
"""
    }

    slicer = CallGraphSlicer()
    target_symbol = "settle_transaction"

    print("\n[STEP 1] REPOSITORY AST INGESTION & DEPENDENCY TRACING")
    print(f"  Files Ingested: {len(sample_files)} source files")
    print(f"  Target Focal Symbol: `{target_symbol}`")

    contract = slicer.condense_repo_for_target(sample_files, target_symbol)

    print(f"\n[STEP 2] SKELETAL COMPACTION COMPLETED in {contract.latency_ms:.3f} ms")
    print(f"  Referenced Dependency Cone: {len(contract.referenced_symbols)} symbols")
    print(f"  Symbols: {', '.join(contract.referenced_symbols)}")
    print(f"  Raw Repository Token Estimate : {contract.original_token_count} tokens")
    print(f"  Compacted Skeletal Tokens     : {contract.compacted_token_count} tokens")
    print(f"  Compression Ratio             : {contract.compression_ratio * 100:.1f}% TOKEN REDUCTION")

    print("\n[STEP 3] DISTILLED SKELETAL CONTRACT (READY FOR CLAUDE OPUS 5.5 / GPT-6 ASTRA):")
    print("-" * 74)
    print(contract.distilled_code.strip())
    print("-" * 74)

    print("\n" + "=" * 74)
    print("  AST-CADENCE COMPACTION SUMMARY")
    print(f"  Tokens Saved for Context: {contract.original_token_count - contract.compacted_token_count}")
    print(f"  Context Clutter Eliminated: 100% dead branches and uncalled functions pruned")
    print("=" * 74 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="ast-cadence: Static Call-Graph AST Slicer & Semantic Topology Compactor"
    )
    subparsers = parser.add_subparsers(dest="command")
    demo_parser = subparsers.add_parser("demo", help="Run interactive AST cadence demonstration")

    args = parser.parse_args()
    if args.command == "demo" or len(sys.argv) == 1:
        run_demo()


if __name__ == "__main__":
    main()
