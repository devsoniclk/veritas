"""Counterparty verification demo."""

from veritas.commit import CommitmentEngine
from veritas.anchor.base_chain import BaseAnchor
from veritas.verifier import Verifier


def main():
    # Simulate receiving a proof bundle from the oracle
    proof_bundle = {
        "output": "$3,421.57",
        "commitment": None,  # Will be computed
        "anchor_tx": None,   # Will be set
        "chain": "base",
        "model_id": "gpt-4o",
    }

    engine = CommitmentEngine()

    # First, simulate the oracle producing the commitment
    commitment = engine.compute("gpt-4o", {"temperature": 0}, "What is the current ETH/USD price?", "$3,421.57")
    proof_bundle["commitment"] = commitment.hex()

    # Simulate anchoring
    anchor = BaseAnchor()
    result = anchor.anchor(commitment)
    proof_bundle["anchor_tx"] = result.tx_hash

    print("[Counterparty] Received proof bundle:")
    print(f"  Output: {proof_bundle['output']}")
    print(f"  Commitment: {proof_bundle['commitment']}")
    print(f"  Anchor Tx: {proof_bundle['anchor_tx']}")

    # Verify
    verifier = Verifier()
    verification = verifier.verify(
        output=proof_bundle["output"],
        commitment=commitment,
        model_id=proof_bundle["model_id"],
        params={"temperature": 0},
        prompt="What is the current ETH/USD price?",
        anchor_tx=proof_bundle["anchor_tx"],
        anchor_backend=anchor,
    )

    print(f"\n[Counterparty] Verification result:")
    print(f"  Valid: {verification.valid}")
    for check in verification.checks_passed:
        print(f"  ✓ {check}")
    for check in verification.checks_failed:
        print(f"  ✗ {check}")

    # Demonstrate tamper detection
    print("\n[Counterparty] Testing tamper detection...")
    tampered = verifier.verify(
        output="WRONG OUTPUT",
        commitment=commitment,
        model_id="gpt-4o",
        params={"temperature": 0},
        prompt="What is the current ETH/USD price?",
    )
    print(f"  Valid: {tampered.valid}")
    for check in tampered.checks_failed:
        print(f"  ✗ {check}")


if __name__ == "__main__":
    main()
