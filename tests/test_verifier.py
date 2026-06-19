"""Tests for the Verifier."""

from veritas.commit import CommitmentEngine
from veritas.verifier import Verifier
from veritas.anchor.base_chain import BaseAnchor


def test_verify_valid_with_context():
    engine = CommitmentEngine()
    commitment = engine.compute("gpt-4o", {"temp": 0}, "hi", "hello")
    verifier = Verifier()
    result = verifier.verify(
        output="hello",
        commitment=commitment,
        model_id="gpt-4o",
        params={"temp": 0},
        prompt="hi",
    )
    assert result.valid
    assert "commitment:output_matches" in result.checks_passed


def test_verify_invalid_output():
    engine = CommitmentEngine()
    commitment = engine.compute("gpt-4o", {"temp": 0}, "hi", "hello")
    verifier = Verifier()
    result = verifier.verify(
        output="wrong",
        commitment=commitment,
        model_id="gpt-4o",
        params={"temp": 0},
        prompt="hi",
    )
    assert not result.valid
    assert "commitment:output_mismatch" in result.checks_failed


def test_verify_with_anchor():
    engine = CommitmentEngine()
    commitment = engine.compute("m", {}, "p", "o")
    anchor = BaseAnchor()
    anchor_result = anchor.anchor(commitment)

    verifier = Verifier()
    result = verifier.verify(
        output="o",
        commitment=commitment,
        model_id="m",
        params={},
        prompt="p",
        anchor_tx=anchor_result.tx_hash,
        anchor_backend=anchor,
    )
    assert result.valid
    assert "anchor:verified_on_chain" in result.checks_passed


def test_verify_with_bad_anchor():
    engine = CommitmentEngine()
    commitment = engine.compute("m", {}, "p", "o")
    anchor = BaseAnchor()

    verifier = Verifier()
    result = verifier.verify(
        output="o",
        commitment=commitment,
        model_id="m",
        params={},
        prompt="p",
        anchor_tx="0xbad",
        anchor_backend=anchor,
    )
    assert not result.valid
    assert "anchor:tx_not_found_or_mismatch" in result.checks_failed


def test_verify_hex_commitment():
    engine = CommitmentEngine()
    commitment = engine.compute("m", {}, "p", "o")
    verifier = Verifier()
    result = verifier.verify(
        output="o",
        commitment=commitment.hex(),
        model_id="m",
        params={},
        prompt="p",
    )
    assert result.valid


def test_verify_quick():
    """verify_quick hashes just the output - so both sides must agree on that convention."""
    import hashlib
    # Quick mode: commitment = SHA256(output)
    output = "o"
    commitment = hashlib.sha256(output.encode()).digest()
    verifier = Verifier()
    assert verifier.verify_quick(output, commitment)
    assert not verifier.verify_quick("wrong", commitment)
