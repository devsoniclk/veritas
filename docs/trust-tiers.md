# Trust Tiers: Honest Comparison

## Overview

Veritas supports three trust tiers, each with different guarantees, costs, and limitations. This document provides an honest assessment so you can pick the right tier for your threat model.

## Comparison Table

| Property | Commit-Only | TEE | ZK |
|----------|------------|-----|-----|
| **Cost** | Free (just hashing) | Moderate (hardware required) | High (proof generation) |
| **Latency** | <1ms | ~100ms | Seconds to minutes |
| **Trust assumption** | Operator is honest | Hardware vendor is honest | Math is correct |
| **Tamper-evidence** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Model identity proof** | ❌ No | ✅ Yes | ✅ Yes |
| **Correctness proof** | ❌ No | ⚠️ Partial (code hash) | ✅ Yes (circuit) |
| **Verifiable by anyone** | ✅ (recompute hash) | ✅ (verify quote) | ✅ (verify proof) |
| **Status** | Implemented | Interface only | Interface only |

## Detailed Analysis

### Commit-Only (Tier 1)

**What it does:** Computes SHA-256 over the canonical inference record (model, params, prompt, output) and stores it in an append-only JSONL log with Merkle batching.

**What it proves:**
- The output existed at a specific time
- The output has not been modified since commitment
- The commitment was anchored on-chain at a specific block

**What it does NOT prove:**
- Which model actually produced the output (the operator could lie about model_id)
- That the model weights are authentic
- That the inference was performed correctly

**When to use it:**
- Low-stakes environments where tamper-evidence is sufficient
- Auditing/logging where you trust the operator
- When you need the cheapest possible solution
- As a building block alongside other trust mechanisms

**Attack vectors:**
- Operator commits a fabricated output with a false model_id
- Operator uses a different (cheaper) model than claimed

### TEE Attestation (Tier 2)

**What it does:** Runs inference inside a Trusted Execution Environment (Intel SGX, AWS Nitro, etc.) and produces a hardware attestation report that proves the code ran correctly.

**What it proves:**
- Everything commit-only proves, PLUS
- The inference ran inside a genuine TEE
- The code (model + inference logic) matches a known measurement
- The output was not observed or modified outside the enclave

**What it does NOT prove:**
- That the model weights themselves are "correct" or well-trained
- That the TEE hardware has no vulnerabilities
- That the prompt wasn't adversarially crafted to exploit the model

**When to use it:**
- When you need to prove which code ran
- Medium-stakes environments (DeFi oracles, agent-to-agent contracts)
- When hardware trust assumptions are acceptable

**Attack vectors:**
- TEE side-channel attacks (Spectre, Foreshadow, etc.)
- Compromised TEE firmware
- The model weights inside the enclave could still be manipulated by the operator before sealing

### ZK Proof (Tier 3)

**What it does:** Expresses model inference as an arithmetic circuit and generates a zero-knowledge proof that the computation was performed correctly.

**What it proves:**
- Everything TEE proves, PLUS
- The inference was mathematically correct (per the circuit)
- No trust in hardware is required
- The proof is publicly verifiable without revealing the model weights

**What it does NOT prove:**
- That the circuit faithfully represents the model (circuit bugs possible)
- That the model weights are "good" (correct inference of wrong model is still wrong)
- Practical limits on model size (current zkML can handle small models only)

**When to use it:**
- High-stakes environments (financial settlements, governance)
- When hardware trust is unacceptable
- When mathematical certainty is required
- When model size fits within proving capacity

**Attack vectors:**
- Circuit doesn't faithfully represent the model
- Trusted setup compromise (for SNARK-based systems)
- Bugs in the prover implementation

## Recommendations

| Scenario | Recommended Tier |
|----------|-----------------|
| Logging/auditing | Commit-Only |
| Agent-to-agent trust | Commit-Only or TEE |
| DeFi oracle | TEE |
| Governance/compliance | TEE or ZK |
| Financial settlement | ZK |

## Key Insight

**No tier can prove the model weights are "good" or that the model is "correct."** All tiers prove that a specific computation produced a specific output. The difference is in how much you trust the computation environment.

The strongest guarantee is: "This specific output was produced by this specific code running on this specific input, and here's the proof." But even with ZK, "this specific code" might have bugs, and "this specific model" might produce harmful outputs.

Choose the tier that matches your trust budget and threat model. Don't over-engineer — commit-only is fine for many use cases.
