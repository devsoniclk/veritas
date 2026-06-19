"""Canonical commitment computation for inference outputs."""

import hashlib
import json
from dataclasses import dataclass


@dataclass
class CommitmentEngine:
    """Computes and verifies SHA-256 commitments over canonical inference records."""

    def compute(
        self,
        model_id: str,
        params: dict,
        prompt: str,
        output: str,
    ) -> bytes:
        """Compute SHA-256 commitment over canonical JSON of the inference record.

        The canonical form sorts keys deterministically so the same inputs
        always produce the same hash regardless of dict ordering.
        """
        canonical = json.dumps(
            {"model": model_id, "params": params, "prompt": prompt, "output": output},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return hashlib.sha256(canonical).digest()

    def compute_hex(self, model_id: str, params: dict, prompt: str, output: str) -> str:
        """Same as compute() but returns hex string."""
        return self.compute(model_id, params, prompt, output).hex()

    def verify(self, output: str, commitment: bytes, **kwargs) -> bool:
        """Verify an output against a commitment.

        For commit-only usage where we only have the output and commitment,
        this checks if SHA-256(output) matches. For full verification with
        model_id/params/prompt, pass them as kwargs.

        Returns True if the recomputed commitment matches.
        """
        if "model_id" in kwargs and "params" in kwargs and "prompt" in kwargs:
            expected = self.compute(
                kwargs["model_id"], kwargs["params"], kwargs["prompt"], output
            )
        else:
            # Fallback: hash just the output
            expected = hashlib.sha256(output.encode("utf-8")).digest()
        return expected == commitment

    @staticmethod
    def commitment_to_hex(commitment: bytes) -> str:
        return commitment.hex()

    @staticmethod
    def hex_to_commitment(hex_str: str) -> bytes:
        return bytes.fromhex(hex_str)
