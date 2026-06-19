"""Tests for tamper-evident log."""

import json
import tempfile
from pathlib import Path

from veritas.log import TamperEvidentLog
from veritas.backends.commit_only import CommitOnlyBackend


def make_log(tmp_path):
    return TamperEvidentLog(tmp_path / "test.jsonl")


def test_append_and_get(tmp_path):
    log = make_log(tmp_path)
    backend = CommitOnlyBackend()
    att = backend.record("m", {}, "p", "o")
    entry = log.append(att)
    assert entry["model_id"] == "m"
    assert log.count == 1
    assert len(log.get_entries()) == 1


def test_persistence(tmp_path):
    log = make_log(tmp_path)
    backend = CommitOnlyBackend()
    att = backend.record("m", {}, "p", "o")
    log.append(att)

    # Reload from disk
    log2 = TamperEvidentLog(tmp_path / "test.jsonl")
    assert log2.count == 1
    assert log2.get_entries()[0]["commitment"] == log.get_entries()[0]["commitment"]


def test_merkle_root(tmp_path):
    log = make_log(tmp_path)
    backend = CommitOnlyBackend()
    for i in range(5):
        att = backend.record("m", {}, f"p{i}", f"o{i}")
        log.append(att)
    root = log.get_merkle_root()
    assert len(root) == 32


def test_verify_entry(tmp_path):
    log = make_log(tmp_path)
    backend = CommitOnlyBackend()
    att = backend.record("m", {}, "p", "o")
    log.append(att)
    root = log.get_merkle_root()
    assert log.verify_entry(att.id, root)


def test_get_proof_for_entry(tmp_path):
    log = make_log(tmp_path)
    backend = CommitOnlyBackend()
    att = backend.record("m", {}, "p", "o")
    log.append(att)
    proof = log.get_proof_for_entry(att.id)
    assert proof is not None
    assert isinstance(proof, list)


def test_get_entry_by_id_missing(tmp_path):
    log = make_log(tmp_path)
    assert log.get_entry_by_id("nonexistent") is None
