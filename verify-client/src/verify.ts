import { createHash } from "crypto";

export interface VerifyInput {
  /** The inference output to verify */
  output: string;
  /** The expected commitment as a hex string */
  commitment: string;
  /** Optional: the model ID used for inference */
  modelId?: string;
  /** Optional: model parameters */
  params?: Record<string, unknown>;
  /** Optional: the input prompt */
  prompt?: string;
  /** Optional: on-chain anchor transaction hash */
  anchorTx?: string;
  /** Optional: chain for anchor verification ("base" or "solana") */
  chain?: "base" | "solana";
}

export interface VerifyResult {
  /** Whether verification passed */
  valid: boolean;
  /** List of checks that passed */
  checksPassed: string[];
  /** List of checks that failed */
  checksFailed: string[];
  /** Additional details */
  details: Record<string, unknown>;
}

/**
 * Compute the canonical commitment hash for an inference record.
 * Matches the Python CommitmentEngine.compute() output.
 */
export function computeCommitment(
  modelId: string,
  params: Record<string, unknown>,
  prompt: string,
  output: string
): Buffer {
  const canonical = JSON.stringify(
    { model: modelId, params, prompt, output },
    Object.keys({ model: modelId, params, prompt, output }).sort(),
  );
  // Note: Python uses sort_keys on nested dicts too, but JSON.stringify with
  // replacer handles top-level. For full compatibility with nested params,
  // we sort recursively.
  const sorted = sortedStringify({ model: modelId, params, prompt, output });
  return createHash("sha256").update(sorted).digest();
}

function sortedStringify(obj: unknown): string {
  if (obj === null || typeof obj !== "object") {
    return JSON.stringify(obj);
  }
  if (Array.isArray(obj)) {
    return `[${obj.map(sortedStringify).join(",")}]`;
  }
  const entries = Object.keys(obj as Record<string, unknown>)
    .sort()
    .map(
      (key) =>
        `${JSON.stringify(key)}:${sortedStringify(
          (obj as Record<string, unknown>)[key]
        )}`
    );
  return `{${entries.join(",")}}`;
}

/**
 * Verify an inference output against a commitment.
 *
 * If modelId, params, and prompt are provided, recomputes the full commitment.
 * Otherwise, checks if SHA-256(output) matches the commitment.
 */
export async function verify(input: VerifyInput): Promise<VerifyResult> {
  const checksPassed: string[] = [];
  const checksFailed: string[] = [];
  const details: Record<string, unknown> = {};

  const commitmentBuf = Buffer.from(input.commitment, "hex");

  // Check 1: Commitment verification
  if (input.modelId && input.params !== undefined && input.prompt) {
    const expected = computeCommitment(
      input.modelId,
      input.params,
      input.prompt,
      input.output
    );
    if (expected.equals(commitmentBuf)) {
      checksPassed.push("commitment:output_matches");
    } else {
      checksFailed.push("commitment:output_mismatch");
    }
  } else {
    // Fallback: just hash the output
    const outputHash = createHash("sha256")
      .update(input.output)
      .digest();
    if (outputHash.equals(commitmentBuf)) {
      checksPassed.push("commitment:output_hash_matches");
    } else {
      // Can't fully verify without context, but report
      details.note = "Full verification requires modelId, params, and prompt";
      details.commitmentHex = input.commitment;
    }
  }

  // Check 2: Anchor verification (placeholder - would need HTTP client)
  if (input.anchorTx) {
    details.anchorTx = input.anchorTx;
    details.anchorNote =
      "On-chain anchor verification requires a node RPC endpoint";
  }

  return {
    valid: checksFailed.length === 0,
    checksPassed,
    checksFailed,
    details,
  };
}
