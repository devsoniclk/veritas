"""Oracle demo - publishes provable outputs."""

import json
from veritas.commit import CommitmentEngine
from veritas.backends.commit_only import CommitOnlyBackend
from veritas.log import TamperEvidentLog
from veritas.anchor.base_chain import BaseAnchor


def main():
    engine = CommitmentEngine()
    backend = CommitOnlyBackend()
    log = TamperEvidentLog()

    # Simulate an oracle that computes an output
    model = "gpt-4o"
    params = {"temperature": 0, "max_tokens": 100}
    prompt = "What is the current ETH/USD price?"
    output = "$3,421.57"

    # Step 1: Record the inference
    attestation = backend.record(model, params, prompt, output)
    entry = log.append(attestation)

    print(f"[Oracle] Recorded inference:")
    print(f"  Commitment: {entry['commitment']}")
    print(f"  Model: {model}")
    print(f"  Output: {output}")

    # Step 2: Anchor on-chain
    root = log.get_merkle_root()
    anchor_backend = BaseAnchor()
    result = anchor_backend.anchor(root, {"entry_count": log.count})

    print(f"\n[Oracle] Anchored on Base:")
    print(f"  Tx Hash: {result.tx_hash}")
    print(f"  Root: {root.hex()}")

    # Step 3: Publish proof bundle
    proof_bundle = {
        "output": output,
        "commitment": entry["commitment"],
        "anchor_tx": result.tx_hash,
        "chain": "base",
        "model_id": model,
    }
    print(f"\n[Oracle] Proof bundle for counterparty:")
    print(json.dumps(proof_bundle, indent=2))


if __name__ == "__main__":
    main()
