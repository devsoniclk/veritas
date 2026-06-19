"""Base (EVM) chain anchoring backend.

For MVP: stores anchor records locally and simulates on-chain writes.
In production, this would use viem/ethers to emit an event on a
verifier contract deployed on Base L2.

Expected contract interface:
    event CommitmentAnchored(bytes32 indexed commitment, uint256 timestamp, address indexed sender);
    function anchorCommitment(bytes32 commitment) external;
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Optional

from veritas.anchor.base import AnchorBackend, AnchorResult

DEFAULT_ANCHORS_DIR = Path.home() / ".veritas" / "anchors"


class BaseAnchor(AnchorBackend):
    """Anchors commitments on Base (EVM) chain.

    MVP implementation: stores anchor records locally as JSON.
    Production: would use viem/ethers to call a contract on Base L2.
    """

    def __init__(self, anchors_dir: Optional[Path] = None, rpc_url: str = ""):
        self.anchors_dir = anchors_dir or DEFAULT_ANCHORS_DIR
        self.anchors_dir.mkdir(parents=True, exist_ok=True)
        self.rpc_url = rpc_url
        self._anchors_file = self.anchors_dir / "base_anchors.json"
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
        return "base"

    def anchor(self, commitment: bytes, metadata: dict | None = None) -> AnchorResult:
        """Anchor a commitment locally (MVP) or on Base L2 (production).

        In MVP mode, we simulate a tx hash and store locally.
        """
        commitment_hex = commitment.hex()
        # Simulate tx hash from commitment + timestamp
        ts = time.time()
        tx_input = f"{commitment_hex}:{ts}"
        tx_hash = "0x" + hashlib.sha256(tx_input.encode()).hexdigest()

        block_number = len(self._records) + 1  # simulated

        record = {
            "tx_hash": tx_hash,
            "commitment": commitment_hex,
            "block_number": block_number,
            "timestamp": ts,
            "chain": "base",
            "metadata": metadata or {},
        }
        self._records[tx_hash] = record
        self._save()

        return AnchorResult(
            tx_hash=tx_hash,
            chain="base",
            block_number=block_number,
            timestamp=ts,
            commitment=commitment,
            metadata={"mode": "local-mvp", **(metadata or {})},
        )

    def verify(self, tx_hash: str, commitment: bytes) -> bool:
        """Verify that a commitment was anchored in a specific tx."""
        record = self._records.get(tx_hash)
        if not record:
            return False
        return record["commitment"] == commitment.hex()

    def get_anchors(self) -> list[dict]:
        """List all anchor records."""
        return list(self._records.values())
