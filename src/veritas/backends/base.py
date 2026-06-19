"""Abstract backend interface for attestation."""

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Attestation:
    """An attestation that an inference was performed."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    commitment: bytes = b""
    model_id: str = ""
    timestamp: float = field(default_factory=time.time)
    backend_type: str = "unknown"
    proof_data: dict = field(default_factory=dict)


class AttestationBackend(ABC):
    """Abstract base class for attestation backends.

    Each backend implements a different trust tier:
    - CommitOnlyBackend: cheapest, tamper-evidence only
    - TEEBackend: hardware-backed attestation
    - ZKBackend: cryptographic proof of correct inference
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Backend identifier string."""
        ...

    @abstractmethod
    def record(
        self,
        model_id: str,
        params: dict,
        prompt: str,
        output: str,
    ) -> Attestation:
        """Record an inference and produce an attestation."""
        ...

    @abstractmethod
    def verify(self, attestation: Attestation, output: str, **kwargs) -> bool:
        """Verify an attestation against an output."""
        ...
