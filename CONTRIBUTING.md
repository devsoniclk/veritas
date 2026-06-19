# Contributing to Veritas

## Getting Started

```bash
git clone <repo-url>
cd veritas
pip install -e ".[dev]"
```

## Development

```bash
# Run tests
pytest tests/ -v

# Type checking
mypy src/veritas/

# Lint
ruff check src/ tests/
```

## Pull Request Process

1. Fork the repo and create a feature branch
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation if needed
5. Open a PR with a clear description

## Architecture Decisions

- **Commitments use SHA-256** over canonical JSON (sorted keys, no whitespace)
- **Merkle trees** use power-of-2 padding with zero-leaf duplication
- **Backends** are pluggable via the `AttestationBackend` ABC
- **Anchors** are pluggable via the `AnchorBackend` ABC
- **CLI** uses Click for composability

## Areas Needing Help

- TEE backend (Intel SGX / AWS Nitro integration)
- ZK proof backend (integration with zkML stacks)
- On-chain contract development (Base L2 verifier contract)
- Agent framework plugins
