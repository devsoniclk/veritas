"""Abstract anchor interface for on-chain commitment anchoring."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import time


@dataclass
class AnchorResult:
    """Result of anchoring a commitment on-chain."""

    tx_hash: str
    chain: str
    block_number: int = 0
    timestamp: float = field(default_factory=time.time)
    commitment: bytes = b""
    metadata: dict = field(default_factory=dict)


class AnchorBackend(ABC):
    """Abstract base class for on-chain anchoring backends.

    Anchoring puts a commitment (or Merkle root) on a public blockchain,
    creating an immutable timestamp that proves the commitment existed
    at a specific point in time.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Backend identifier string."""
        ...

    @abstractmethod
    def anchor(self, commitment: bytes, metadata: dict | None = None) -> AnchorResult:
        """Anchor a commitment (or Merkle root) on-chain."""
        ...

    @abstractmethod
    def verify(self, tx_hash: str, commitment: bytes) -> bool:
        """Verify that a commitment was anchored in a specific transaction."""
        ...
