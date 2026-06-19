"""Tamper-evident JSONL log with Merkle batching."""

import json
import os
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from veritas.backends.base import Attestation
from veritas.merkle import PositionalMerkleTree


DEFAULT_LOG_DIR = Path.home() / ".veritas"
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "log.jsonl"


class TamperEvidentLog:
    """Append-only JSONL log that batches entries into Merkle trees for anchoring."""

    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or DEFAULT_LOG_FILE
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list[dict] = []
        self._load()

    def _load(self):
        if self.log_path.exists():
            with open(self.log_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self._entries.append(json.loads(line))

    def append(self, attestation: Attestation) -> dict:
        """Append an attestation to the log and return the log entry."""
        entry = {
            "id": attestation.id,
            "timestamp": attestation.timestamp,
            "commitment": attestation.commitment.hex(),
            "model_id": attestation.model_id,
            "backend_type": attestation.backend_type,
            "metadata": attestation.proof_data,
        }
        self._entries.append(entry)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry

    def get_entries(self) -> list[dict]:
        return list(self._entries)

    def get_entry_by_id(self, entry_id: str) -> Optional[dict]:
        for entry in self._entries:
            if entry["id"] == entry_id:
                return entry
        return None

    def build_merkle_tree(self) -> PositionalMerkleTree:
        """Build a Merkle tree from all log entries."""
        if not self._entries:
            raise ValueError("Log is empty, cannot build Merkle tree")
        leaves = [bytes.fromhex(e["commitment"]) for e in self._entries]
        return PositionalMerkleTree(leaves)

    def get_merkle_root(self) -> bytes:
        tree = self.build_merkle_tree()
        return tree.root

    def verify_entry(self, entry_id: str, root: bytes) -> bool:
        """Verify that an entry is included in a Merkle root."""
        entry = self.get_entry_by_id(entry_id)
        if not entry:
            return False
        tree = self.build_merkle_tree()
        idx = next(
            (i for i, e in enumerate(self._entries) if e["id"] == entry_id), None
        )
        if idx is None:
            return False
        leaf = bytes.fromhex(entry["commitment"])
        proof = tree.get_proof(idx)
        return PositionalMerkleTree.verify_proof(leaf, proof, root)

    def get_proof_for_entry(self, entry_id: str) -> Optional[list[tuple[bytes, str]]]:
        """Get the Merkle proof for a specific entry."""
        idx = next(
            (i for i, e in enumerate(self._entries) if e["id"] == entry_id), None
        )
        if idx is None:
            return None
        tree = self.build_merkle_tree()
        return tree.get_proof(idx)

    @property
    def count(self) -> int:
        return len(self._entries)
