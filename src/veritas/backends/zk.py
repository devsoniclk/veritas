"""ZK (Zero-Knowledge) proof backend.

This is the highest-cost, strongest-trust tier. It proves:
- The inference was computed correctly according to a public circuit
- No one (not even the prover) could have forged the output
- The model weights used match a public commitment

Expected integration flow:
1. Model inference is expressed as an arithmetic circuit
2. A zkML prover generates a proof that the circuit was executed correctly
3. Veritas wraps the proof into an Attestation
4. Verifier checks the proof against the public verification key

Status: INTERFACE ONLY - requires integration with zkML proving stacks
(e.g., EZKL, Modulus, Risc Zero, or custom circuits).
"""

from veritas.backends.base import Attestation, AttestationBackend


class ZKBackend(AttestationBackend):
    """ZK proof-based attestation backend (stub).

    This backend requires a zero-knowledge proving system to function.
    Expected to integrate with zkML stacks such as:
    - EZKL (ONNX model proving)
    - Risc Zero (RISC-V zkVM)
    - Modulus (custom zkML)
    - Custom Groth16/PLONK circuits

    To implement:
    1. Express model inference as an arithmetic circuit
    2. Generate proof using a zkML prover
    3. Return proof and public inputs as proof_data
    """

    def __init__(self, prover: str = "ezkl"):
        self.prover = prover

    @property
    def name(self) -> str:
        return f"zk-{self.prover}"

    def record(
        self,
        model_id: str,
        params: dict,
        prompt: str,
        output: str,
    ) -> Attestation:
        raise NotImplementedError(
            f"ZK backend '{self.prover}' is not yet implemented.\n"
            f"Expected flow:\n"
            f"  1. Express model inference as arithmetic circuit\n"
            f"  2. Generate proof via {self.prover} prover\n"
            f"  3. Return proof + public inputs\n"
            f"Integration targets: EZKL, Risc Zero, Modulus\n"
        )

    def verify(self, attestation: Attestation, output: str, **kwargs) -> bool:
        raise NotImplementedError(
            f"ZK verification for '{self.prover}' is not yet implemented.\n"
            f"Expected: verify ZK proof against public verification key.\n"
        )
