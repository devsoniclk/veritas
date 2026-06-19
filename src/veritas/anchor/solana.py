"""Solana anchoring backend.

For MVP: stores anchor records locally and simulates on-chain writes.
In production, this would use Solana web3.js or a Rust client to
write a commitment to a Solana program.

Expected program interface:
    - Instruction: anchor_commitment(commitment: [u8; 32])
    - Account: stores commitment, timestamp, and sender pubkey
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Optional

from veritas.anchor.base import AnchorBackend, AnchorResult

DEFAULT_ANCHORS_DIR = Path.home() / ".veritas" / "anchors"


class SolanaAnchor(AnchorBackend):
    """Anchors commitments on Solana.

    MVP implementation: stores anchor records locally as JSON.
    Production: would use @solana/web3.js or Anchor to call a program.
    """

    def __init__(self, anchors_dir: Optional[Path] = None, rpc_url: str = ""):
        self.anchors_dir = anchors_dir or DEFAULT_ANCHORS_DIR
        self.anchors_dir.mkdir(parents=True, exist_ok=True)
        self.rpc_url = rpc_url
        self._anchors_file = self.anchors_dir / "solana_anchors.json"
        self._load()

    def _load(self):
        if self._anchors_file.exists():
            with open(self._anchors_file) as f:
                self._records = json.load(f)
        else:
            self._records = {}

    def _save(self):
        with open(self._anchors_file, "w") as f:
            json.dump(self._records, f, indent=2, sort_keys=True)

    @property
    def name(self) -> str:
        return "solana"

    def anchor(self, commitment: bytes, metadata: dict | None = None) -> AnchorResult:
        commitment_hex = commitment.hex()
        ts = time.time()
        tx_input = f"{commitment_hex}:{ts}"
        # Simulate Solana signature (base58-like hex)
        sig = hashlib.sha256(tx_input.encode()).hexdigest()

        slot = len(self._records) + 1

        record = {
            "signature": sig,
            "commitment": commitment_hex,
            "slot": slot,
            "timestamp": ts,
            "chain": "solana",
            "metadata": metadata or {},
        }
        self._records[sig] = record
        self._save()

        return AnchorResult(
            tx_hash=sig,
            chain="solana",
            block_number=slot,
            timestamp=ts,
            commitment=commitment,
            metadata={"mode": "local-mvp", **(metadata or {})},
        )

    def verify(self, tx_hash: str, commitment: bytes) -> bool:
        record = self._records.get(tx_hash)
        if not record:
            return False
        return record["commitment"] == commitment.hex()

    def get_anchors(self) -> list[dict]:
        return list(self._records.values())
