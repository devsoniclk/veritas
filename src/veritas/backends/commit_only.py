"""Commit-only attestation backend.

This is the cheapest and weakest trust tier. It proves:
- The output was committed at a specific time (tamper-evidence)
- The output has not been changed since commitment

It does NOT prove:
- Which model actually produced the output
- That the inference was performed correctly
- That the model weights are authentic

Use this tier when tamper-evidence is sufficient and you trust the
operator to not forge commitments.
"""

from veritas.backends.base import Attestation, AttestationBackend
from veritas.commit import CommitmentEngine


class CommitOnlyBackend(AttestationBackend):
    """Tamper-evident log backend. Computes commitment and stores it."""

    def __init__(self):
        self._engine = CommitmentEngine()

    @property
    def name(self) -> str:
        return "commit-only"

    def record(
        self,
        model_id: str,
        params: dict,
        prompt: str,
        output: str,
    ) -> Attestation:
        commitment = self._engine.compute(model_id, params, prompt, output)
        return Attestation(
            commitment=commitment,
            model_id=model_id,
            backend_type=self.name,
            proof_data={
                "params": params,
                "prompt_hash": CommitmentEngine.commitment_to_hex(
                    __import__("hashlib").sha256(prompt.encode()).digest()
                ),
            },
        )

    def verify(self, attestation: Attestation, output: str, **kwargs) -> bool:
        """Verify by recomputing commitment from stored proof_data."""
        params = attestation.proof_data.get("params", {})
        prompt = kwargs.get("prompt", "")
        expected = self._engine.compute(
            attestation.model_id, params, prompt, output
        )
        return expected == attestation.commitment
