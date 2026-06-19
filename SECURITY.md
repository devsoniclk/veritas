# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability in Veritas, please report it responsibly:

1. **Do NOT open a public issue.**
2. Email security concerns to the maintainers (see README for contact).
3. Include a description, reproduction steps, and potential impact.
4. We aim to acknowledge within 48 hours and provide a fix timeline.

## Threat Model

Veritas operates in adversarial multi-agent environments where:
- An agent may lie about which model produced an output
- An agent may tamper with committed outputs after the fact
- The commitment log could be modified if stored insecurely

### What Veritas protects against (commit-only tier):
- **Tampering**: Output changed after commitment (detected via hash mismatch)
- **Backdating**: Commitment timestamp manipulation (detected via append-only log + Merkle anchoring)

### What Veritas does NOT protect against (commit-only tier):
- **Model impersonation**: We cannot prove which model ran without TEE/ZK
- **Prompt injection**: The prompt itself is committed but not validated
- **Log deletion**: If the log file is deleted, commitments are lost (use on-chain anchoring)

## Best Practices

1. **Always anchor Merkle roots on-chain** for production use
2. **Use TEE or ZK tiers** when model identity matters
3. **Store logs in append-only storage** (e.g., S3 with object lock)
4. **Verify before acting** on any agent output in adversarial settings
