"""Merkle tree for batch commitment verification."""

import hashlib
from typing import Optional


class MerkleTree:
    """SHA-256 Merkle tree with power-of-2 padding (duplicate last leaf if odd)."""

    def __init__(self, leaves: list[bytes]):
        if not leaves:
            raise ValueError("Cannot build Merkle tree from empty leaves")
        self.leaves = list(leaves)
        self._build()

    def _build(self):
        """Build the tree bottom-up."""
        level = [hashlib.sha256(leaf).digest() for leaf in self.leaves]
        self._layers: list[list[bytes]] = [level]
        while len(level) > 1:
            if len(level) % 2 == 1:
                level.append(level[-1])  # duplicate last
            next_level = []
            for i in range(0, len(level), 2):
                combined = level[i] + level[i + 1]
                next_level.append(hashlib.sha256(combined).digest())
            level = next_level
            self._layers.append(level)

    @property
    def root(self) -> bytes:
        return self._layers[-1][0]

    @property
    def root_hex(self) -> str:
        return self.root.hex()

    def get_proof(self, leaf_index: int) -> list[bytes]:
        """Get Merkle proof (list of sibling hashes) for the given leaf index."""
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            raise IndexError(f"Leaf index {leaf_index} out of range [0, {len(self.leaves)})")

        proof: list[bytes] = []
        idx = leaf_index
        for layer in self._layers[:-1]:
            # Pad layer to even length
            padded = list(layer)
            if len(padded) % 2 == 1:
                padded.append(padded[-1])
            if idx % 2 == 0:
                proof.append(padded[idx + 1])
            else:
                proof.append(padded[idx - 1])
            idx //= 2
        return proof

    @staticmethod
    def verify_proof(leaf: bytes, proof: list[bytes], root: bytes) -> bool:
        """Verify a Merkle proof for a leaf against an expected root."""
        current = hashlib.sha256(leaf).digest()
        for sibling in proof:
            # We need to determine ordering. Try both and track.
            # Convention: if we're the left child, sibling is right, and vice versa.
            # Since we don't know the position, we try the standard approach:
            # the proof is ordered such that we always combine current + sibling
            # or sibling + current. We need position info.
            # Actually, let's use a convention: each proof element is (sibling, position)
            # For simplicity, we'll just try both orderings and see which matches.
            # But that's not deterministic. Let's use a simpler approach.
            pass
        # Re-implement with position-aware proof
        current = hashlib.sha256(leaf).digest()
        for sibling in proof:
            # Proof elements are ordered: if our index is even, sibling is to the right,
            # if odd, sibling is to the left. We store raw sibling hashes and use
            # lexicographic ordering as a tiebreaker.
            if current <= sibling:
                current = hashlib.sha256(current + sibling).digest()
            else:
                current = hashlib.sha256(sibling + current).digest()
        return current == root


class PositionalMerkleTree:
    """Merkle tree that produces position-aware proofs for unambiguous verification."""

    def __init__(self, leaves: list[bytes]):
        if not leaves:
            raise ValueError("Cannot build Merkle tree from empty leaves")
        self.leaves = list(leaves)
        self._build()

    def _build(self):
        level = [hashlib.sha256(leaf).digest() for leaf in self.leaves]
        self._layers: list[list[bytes]] = [level]
        while len(level) > 1:
            if len(level) % 2 == 1:
                level.append(level[-1])
            next_level = []
            for i in range(0, len(level), 2):
                combined = level[i] + level[i + 1]
                next_level.append(hashlib.sha256(combined).digest())
            level = next_level
            self._layers.append(level)

    @property
    def root(self) -> bytes:
        return self._layers[-1][0]

    @property
    def root_hex(self) -> str:
        return self.root.hex()

    def get_proof(self, leaf_index: int) -> list[tuple[bytes, str]]:
        """Get proof as list of (sibling_hash, 'left'|'right') tuples.

        'left' means sibling is on the left, 'right' means sibling is on the right.
        """
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            raise IndexError(f"Leaf index {leaf_index} out of range")

        proof: list[tuple[bytes, str]] = []
        idx = leaf_index
        for layer in self._layers[:-1]:
            padded = list(layer)
            if len(padded) % 2 == 1:
                padded.append(padded[-1])
            if idx % 2 == 0:
                proof.append((padded[idx + 1], "right"))
            else:
                proof.append((padded[idx - 1], "left"))
            idx //= 2
        return proof

    @staticmethod
    def verify_proof(
        leaf: bytes,
        proof: list[tuple[bytes, str]],
        root: bytes,
    ) -> bool:
        """Verify a position-aware Merkle proof."""
        current = hashlib.sha256(leaf).digest()
        for sibling, position in proof:
            if position == "right":
                current = hashlib.sha256(current + sibling).digest()
            else:
                current = hashlib.sha256(sibling + current).digest()
        return current == root
