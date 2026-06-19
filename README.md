# veritas

Agent A calls a model and passes the output to Agent B. Agent B has no way to verify that output actually came from the model it claims, or that it wasn't modified in transit.

Veritas makes inference provable. You commit the output at inference time, optionally anchor the commitment on-chain, and the verifier can later confirm the output matches the commitment.

---

The honest version of what each tier actually gives you:

| Tier | What it proves | What it doesn't prove | Status |
|------|---------------|----------------------|--------|
| **Commit-only** | This output was committed at this time and hasn't changed since | Which model produced it | ✅ Done |
| **TEE** | Inference ran inside a hardware enclave | That the weights are what they claim | Interface only |
| **ZK** | Inference was computed correctly | Anything about the prompt | Interface only |

Commit-only is free and works today. TEE and ZK backends have the interface defined but aren't implemented — those are hard problems with active research. Veritas gives you the commit tier now and a migration path when the harder tiers become practical.

---

## Usage

```bash
cd veritas && pip install -e ".[dev]"

# record an inference
veritas record --model gpt-4o --prompt "What is 2+2?" --output "4"

# anchor to chain
veritas anchor --log ~/.veritas/log.jsonl --chain base

# verify later
veritas verify --output "4" --commitment <hex>
```

## Python API

```python
from veritas.commit import CommitmentEngine
from veritas.backends.commit_only import CommitOnlyBackend

engine = CommitmentEngine()
commitment = engine.compute("gpt-4o", {"temperature": 0}, "What is 2+2?", "4")
assert engine.verify("4", commitment)

backend = CommitOnlyBackend()
attestation = backend.record("gpt-4o", {}, "What is 2+2?", "4")
assert backend.verify(attestation, "4")
```

## TypeScript verifier

For the consuming agent:

```typescript
import { verify } from "@veritas/verify-client";

const valid = await verify({
  output: "4",
  commitment: "abcdef...",
  anchorTx: "0x...",  // optional — checks on-chain anchor
});
```

## Architecture

The flow is: CommitmentEngine computes a hash of (model, params, prompt, output), AttestationBackend records it to a tamper-evident JSONL log, AnchorBackend optionally writes a Merkle root to chain, and the independent verifier recomputes the commitment and checks it matches.

The verifier is a separate library by design — it has no dependency on the recording side. An agent can verify without trusting the recording infrastructure.

## License

MIT
