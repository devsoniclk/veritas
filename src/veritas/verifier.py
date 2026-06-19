"""Independent verification library."""

from dataclasses import dataclass, field

from veritas.commit import CommitmentEngine


@dataclass
class VerificationResult:
    """Result of a verification check."""

    valid: bool
    checks_passed: list[str] = field(default_factory=list)
    checks_failed: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


class Verifier:
    """Independent verifier for inference commitments.

    Can verify:
    1. Output matches a commitment (recompute hash)
    2. Commitment was anchored on-chain (check anchor tx)
    3. Attestation backend type (if provided)
    """

    def __init__(self):
        self._engine = CommitmentEngine()

    def verify(
        self,
        output: str,
        commitment: bytes | str,
        model_id: str | None = None,
        params: dict | None = None,
        prompt: str | None = None,
        anchor_tx: str | None = None,
        anchor_backend: object | None = None,
        backend_type: str | None = None,
    ) -> VerificationResult:
        """Verify an output against a commitment and optional anchor.

        Args:
            output: The inference output to verify
            commitment: The expected commitment (bytes or hex string)
            model_id: Model identifier (for full recomputation)
            params: Model parameters (for full recomputation)
            prompt: Input prompt (for full recomputation)
            anchor_tx: Transaction hash to check on-chain
            anchor_backend: AnchorBackend instance for tx verification
            backend_type: Expected backend type (e.g., "commit-only")
        """
        passed: list[str] = []
        failed: list[str] = []
        details: dict = {}

        # Normalize commitment
        if isinstance(commitment, str):
            commitment_bytes = bytes.fromhex(commitment)
        else:
            commitment_bytes = commitment

        # Check 1: Commitment verification
        if model_id and params is not None and prompt:
            expected = self._engine.compute(model_id, params, prompt, output)
            if expected == commitment_bytes:
                passed.append("commitment:output_matches")
            else:
                failed.append("commitment:output_mismatch")
        else:
            # Without full context, we can only report the commitment hex
            details["commitment_hex"] = commitment_bytes.hex()

        # Check 2: Anchor verification
        if anchor_tx and anchor_backend:
            try:
                if anchor_backend.verify(anchor_tx, commitment_bytes):
                    passed.append("anchor:verified_on_chain")
                    details["anchor_tx"] = anchor_tx
                else:
                    failed.append("anchor:tx_not_found_or_mismatch")
            except Exception as e:
                failed.append(f"anchor:error:{e}")

        # Check 3: Backend type
        if backend_type:
            if backend_type == "commit-only":
                passed.append("backend:commit-only (weakest tier)")
                details["trust_tier"] = "commit-only"
            elif backend_type.startswith("tee"):
                passed.append(f"backend:{backend_type}")
                details["trust_tier"] = "tee"
            elif backend_type.startswith("zk"):
                passed.append(f"backend:{backend_type}")
                details["trust_tier"] = "zk"

        valid = len(failed) == 0
        return VerificationResult(
            valid=valid,
            checks_passed=passed,
            checks_failed=failed,
            details=details,
        )

    def verify_quick(self, output: str, commitment: bytes) -> bool:
        """Quick check: recompute hash of output and compare."""
        return self._engine.verify(output, commitment)
