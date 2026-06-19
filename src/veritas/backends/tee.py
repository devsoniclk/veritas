"""TEE (Trusted Execution Environment) attestation backend.

This is the moderate-cost, moderate-trust tier. It proves:
- The inference ran inside a hardware enclave (Intel SGX, AWS Nitro, etc.)
- The code that executed matches a known measurement
- The output was not tampered with after enclave execution

Expected integration flow:
1. Enclave loads model weights and performs inference
2. Enclave produces an attestation report (e.g., SGX quote, Nitro attestation doc)
3. Veritas wraps the attestation report into an Attestation object
4. Verifier can check the attestation report against known enclave measurements

Status: INTERFACE ONLY - requires TEE hardware integration to implement.
"""

from veritas.backends.base import Attestation, AttestationBackend


class TEEBackend(AttestationBackend):
    """TEE-based attestation backend (stub).

    This backend requires a Trusted Execution Environment (Intel SGX,
    AWS Nitro Enclave, ARM TrustZone, or similar) to function.

    To implement:
    1. Integrate with your TEE platform's attestation SDK
    2. Run inference inside the enclave
    3. Capture the attestation report
    4. Return it as proof_data in the Attestation
    """

    def __init__(self, platform: str = "sgx"):
        self.platform = platform

    @property
    def name(self) -> str:
        return f"tee-{self.platform}"

    def record(
        self,
        model_id: str,
        params: dict,
        prompt: str,
        output: str,
    ) -> Attestation:
        raise NotImplementedError(
            f"TEE backend '{self.platform}' is not yet implemented.\n"
            f"Expected flow:\n"
            f"  1. Run inference inside a {self.platform} enclave\n"
            f"  2. Enclave produces an attestation report\n"
            f"  3. Veritas wraps the report into an Attestation\n"
            f"Integration targets: Intel SGX, AWS Nitro Enclave\n"
        )

    def verify(self, attestation: Attestation, output: str, **kwargs) -> bool:
        raise NotImplementedError(
            f"TEE verification for '{self.platform}' is not yet implemented.\n"
            f"Expected: verify enclave attestation report against known measurements.\n"
        )
