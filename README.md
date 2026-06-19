# Veritas

**Verifiable inference proofs anchored on-chain.**

An agent acts on another agent's output. How does it know that output really came from the model it claims? Veritas makes inference provable.

---

## Trust-Tier Ladder

```
  ┌─────────────────────────────────────────────────────┐
  │  ZK Proof        │ Strongest guarantee │ Expensive   │
  ├─────────────────────────────────────────────────────┤
  │  TEE Attestation │ Hardware-backed     │ Moderate    │
  ├─────────────────────────────────────────────────────┤
  │  Commit-Only     │ Tamper-evident      │ Cheapest    │
  └─────────────────────────────────────────────────────┘
       ↑ pick the tier that matches your trust budget
```

| Tier | What it proves | Cost | Status |
|------|---------------|------|--------|
| **Commit-only** | Output was committed at a specific time (tamper-evidence). Does NOT prove model identity. | Free | ✅ Implemented |
| **TEE** | Code ran inside a trusted execution environment. | Moderate | 🔧 Interface only |
| **ZK** | Cryptographic proof that inference was performed correctly. | High | 🔧 Interface only |

See [docs/trust-tiers.md](docs/trust-tiers.md) for the full honest comparison.

---

## Quickstart

```bash
# Install
cd veritas && pip install -e ".[dev]"

# 1. Record an inference
veritas record --model gpt-4o --prompt "What is 2+2?" --output "4"

# 2. Anchor the log on-chain (local MVP)
veritas anchor --log ~/.veritas/log.jsonl --chain base

# 3. Verify an output
veritas verify --output "4" --commitment <hex-hash> [--anchor <tx>]

# 4. Check log status
veritas status
```

### Python API

```python
from veritas.commit import CommitmentEngine
from veritas.backends.commit_only import CommitOnlyBackend

engine = CommitmentEngine()
commitment = engine.compute("gpt-4o", {"temperature": 0}, "What is 2+2?", "4")
assert engine.verify("4", commitment)  # recompute and check

backend = CommitOnlyBackend()
attestation = backend.record("gpt-4o", {"temperature": 0}, "What is 2+2?", "4")
assert backend.verify(attestation, "4")
```

### TypeScript Verifier

```ts
import { verify } from "@veritas/verify-client";

const valid = await verify({
  output: "4",
  commitment: "abcdef...",
  anchorTx: "0x...", // optional
});
```

---

## Architecture

```
Agent A                          Agent B
  │                                │
  ├─ inference output              │
  ├─ CommitmentEngine.compute()    │
  ├─ AttestationBackend.record()   │
  ├─ TamperEvidentLog.append()     │
  ├─ AnchorBackend.anchor()        │
  │        (on-chain)              │
  │                                ├─ Verifier.verify(output, commitment, anchor?)
  │                                ├─ checks passed → trust the output
```

---

## Honest Scope

**Veritas proves:**
- A specific output was committed at a specific time
- The output has not been tampered with since commitment
- (With TEE) The inference ran in a hardware enclave
- (With ZK) The inference was computed correctly

**Veritas does NOT prove (commit-only tier):**
- Which model actually produced the output
- That the model weights are what they claim to be
- That the prompt was not adversarially crafted

---

## Roadmap

- [x] Commit-only backend with tamper-evident JSONL log
- [x] Merkle batching for efficient on-chain anchoring
- [x] Base (EVM) and Solana anchor interfaces
- [x] Independent verifier library (Python + TypeScript)
- [x] CLI for record/anchor/verify workflow
- [ ] TEE backend integration (Intel SGX / AWS Nitro)
- [ ] ZK proof backend integration (zkML proving stacks)
- [ ] Production on-chain contracts (Base L2)
- [ ] Agent framework plugins (LangChain, CrewAI)

---

## License

MIT
