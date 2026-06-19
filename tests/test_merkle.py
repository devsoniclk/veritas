"""Tests for Merkle tree."""

import hashlib
import pytest
from veritas.merkle import MerkleTree, PositionalMerkleTree


class TestPositionalMerkleTree:
    def test_single_leaf(self):
        tree = PositionalMerkleTree([b"leaf"])
        root = tree.root
        assert len(root) == 32

    def test_two_leaves(self):
        tree = PositionalMerkleTree([b"a", b"b"])
        root = tree.root
        assert len(root) == 32
        # Root should be SHA256(SHA256(a) + SHA256(b))
        ha = hashlib.sha256(b"a").digest()
        hb = hashlib.sha256(b"b").digest()
        expected = hashlib.sha256(ha + hb).digest()
        assert root == expected

    def test_proof_roundtrip(self):
        leaves = [b"a", b"b", b"c", b"d"]
        tree = PositionalMerkleTree(leaves)
        root = tree.root
        for i, leaf in enumerate(leaves):
            proof = tree.get_proof(i)
            assert PositionalMerkleTree.verify_proof(leaf, proof, root)

    def test_proof_wrong_leaf(self):
        leaves = [b"a", b"b"]
        tree = PositionalMerkleTree(leaves)
        proof = tree.get_proof(0)
        assert not PositionalMerkleTree.verify_proof(b"wrong", proof, tree.root)

    def test_proof_wrong_root(self):
        leaves = [b"a", b"b"]
        tree = PositionalMerkleTree(leaves)
        proof = tree.get_proof(0)
        assert not PositionalMerkleTree.verify_proof(b"a", proof, b"\x00" * 32)

    def test_odd_leaves(self):
        leaves = [b"a", b"b", b"c"]
        tree = PositionalMerkleTree(leaves)
        for i, leaf in enumerate(leaves):
            proof = tree.get_proof(i)
            assert PositionalMerkleTree.verify_proof(leaf, proof, tree.root)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            PositionalMerkleTree([])

    def test_index_out_of_range(self):
        tree = PositionalMerkleTree([b"a"])
        with pytest.raises(IndexError):
            tree.get_proof(1)

    def test_root_hex(self):
        tree = PositionalMerkleTree([b"a"])
        assert len(tree.root_hex) == 64
