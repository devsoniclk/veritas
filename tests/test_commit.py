"""Tests for CommitmentEngine."""

import hashlib
import json
from veritas.commit import CommitmentEngine


def test_compute_deterministic():
    engine = CommitmentEngine()
    c1 = engine.compute("gpt-4o", {"temp": 0}, "hello", "world")
    c2 = engine.compute("gpt-4o", {"temp": 0}, "hello", "world")
    assert c1 == c2


def test_compute_different_output():
    engine = CommitmentEngine()
    c1 = engine.compute("gpt-4o", {"temp": 0}, "hello", "world")
    c2 = engine.compute("gpt-4o", {"temp": 0}, "hello", "other")
    assert c1 != c2


def test_compute_canonical_json():
    engine = CommitmentEngine()
    # Same data, different key order should produce same hash
    c1 = engine.compute("model", {"b": 2, "a": 1}, "prompt", "output")
    c2 = engine.compute("model", {"a": 1, "b": 2}, "prompt", "output")
    assert c1 == c2


def test_compute_hex():
    engine = CommitmentEngine()
    hex_commit = engine.compute_hex("m", {}, "p", "o")
    raw_commit = engine.compute("m", {}, "p", "o")
    assert hex_commit == raw_commit.hex()


def test_verify_with_full_context():
    engine = CommitmentEngine()
    commitment = engine.compute("gpt-4o", {"temp": 0}, "hi", "hello")
    assert engine.verify("hello", commitment, model_id="gpt-4o", params={"temp": 0}, prompt="hi")


def test_verify_wrong_output():
    engine = CommitmentEngine()
    commitment = engine.compute("gpt-4o", {"temp": 0}, "hi", "hello")
    assert not engine.verify("goodbye", commitment, model_id="gpt-4o", params={"temp": 0}, prompt="hi")


def test_commitment_to_hex_roundtrip():
    commitment = b"\x00" * 32
    hex_str = CommitmentEngine.commitment_to_hex(commitment)
    assert CommitmentEngine.hex_to_commitment(hex_str) == commitment
