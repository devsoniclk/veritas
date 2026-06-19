"""Tests for attestation backends."""

import pytest
from veritas.backends.commit_only import CommitOnlyBackend
from veritas.backends.tee import TEEBackend
from veritas.backends.zk import ZKBackend


class TestCommitOnlyBackend:
    def test_record_produces_attestation(self):
        backend = CommitOnlyBackend()
        att = backend.record("gpt-4o", {"temp": 0}, "hi", "hello")
        assert att.model_id == "gpt-4o"
        assert att.backend_type == "commit-only"
        assert len(att.commitment) == 32
        assert att.id  # non-empty

    def test_record_deterministic(self):
        backend = CommitOnlyBackend()
        a1 = backend.record("m", {}, "p", "o")
        a2 = backend.record("m", {}, "p", "o")
        assert a1.commitment == a2.commitment

    def test_verify_valid(self):
        backend = CommitOnlyBackend()
        att = backend.record("gpt-4o", {"temp": 0}, "hi", "hello")
        assert backend.verify(att, "hello", prompt="hi")

    def test_verify_invalid(self):
        backend = CommitOnlyBackend()
        att = backend.record("gpt-4o", {"temp": 0}, "hi", "hello")
        assert not backend.verify(att, "wrong", prompt="hi")


class TestTEEBackend:
    def test_not_implemented(self):
        backend = TEEBackend()
        with pytest.raises(NotImplementedError):
            backend.record("m", {}, "p", "o")


class TestZKBackend:
    def test_not_implemented(self):
        backend = ZKBackend()
        with pytest.raises(NotImplementedError):
            backend.record("m", {}, "p", "o")
