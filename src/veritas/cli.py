"""CLI for Veritas - record, anchor, verify inference proofs."""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from veritas.backends.commit_only import CommitOnlyBackend
from veritas.anchor.base_chain import BaseAnchor
from veritas.anchor.solana import SolanaAnchor
from veritas.commit import CommitmentEngine
from veritas.log import TamperEvidentLog
from veritas.verifier import Verifier

console = Console()


@click.group()
def main():
    """Veritas - Verifiable inference proofs anchored on-chain."""
    pass


@main.command()
@click.option("--model", required=True, help="Model identifier")
@click.option("--prompt", required=True, help="Input prompt")
@click.option("--output", required=True, help="Inference output")
@click.option("--params", default="{}", help="Model parameters (JSON)")
@click.option("--backend", default="commit", type=click.Choice(["commit", "tee", "zk"]))
@click.option("--log", "log_path", default=None, help="Log file path")
def record(model, prompt, output, params, backend, log_path):
    """Record an inference commitment."""
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError:
        console.print("[red]Error: --params must be valid JSON[/red]")
        sys.exit(1)

    if backend == "commit":
        backend_inst = CommitOnlyBackend()
    elif backend == "tee":
        console.print("[yellow]TEE backend not yet implemented[/yellow]")
        sys.exit(1)
    elif backend == "zk":
        console.print("[yellow]ZK backend not yet implemented[/yellow]")
        sys.exit(1)

    attestation = backend_inst.record(model, params_dict, prompt, output)

    log = TamperEvidentLog(Path(log_path) if log_path else None)
    entry = log.append(attestation)

    console.print("[green]✓ Inference recorded[/green]")
    console.print(f"  ID:         {entry['id']}")
    console.print(f"  Commitment: {entry['commitment']}")
    console.print(f"  Model:      {entry['model_id']}")
    console.print(f"  Backend:    {entry['backend_type']}")
    console.print(f"  Log:        {log.log_path}")


@main.command()
@click.option("--log", "log_path", default=None, help="Log file path")
@click.option("--chain", default="base", type=click.Choice(["base", "solana"]))
def anchor(log_path, chain):
    """Anchor the log's Merkle root on-chain."""
    log = TamperEvidentLog(Path(log_path) if log_path else None)

    if log.count == 0:
        console.print("[red]Error: Log is empty, nothing to anchor[/red]")
        sys.exit(1)

    root = log.get_merkle_root()

    if chain == "base":
        anchor_backend = BaseAnchor()
    elif chain == "solana":
        anchor_backend = SolanaAnchor()

    result = anchor_backend.anchor(root, {"entry_count": log.count})

    console.print("[green]✓ Merkle root anchored[/green]")
    console.print(f"  Chain:      {result.chain}")
    console.print(f"  Tx Hash:    {result.tx_hash}")
    console.print(f"  Block:      {result.block_number}")
    console.print(f"  Root:       {root.hex()}")
    console.print(f"  Entries:    {log.count}")


@main.command()
@click.option("--output", required=True, help="Output to verify")
@click.option("--commitment", required=True, help="Expected commitment (hex)")
@click.option("--model", default=None, help="Model ID for full verification")
@click.option("--params", default="{}", help="Model params (JSON)")
@click.option("--prompt", default=None, help="Original prompt")
@click.option("--anchor", "anchor_tx", default=None, help="Anchor tx hash")
@click.option("--chain", default="base", type=click.Choice(["base", "solana"]))
def verify(output, commitment, model, params, prompt, anchor_tx, chain):
    """Verify an output against a commitment."""
    verifier = Verifier()
    commitment_bytes = bytes.fromhex(commitment)

    params_dict = json.loads(params)

    anchor_backend = None
    if anchor_tx:
        anchor_backend = BaseAnchor() if chain == "base" else SolanaAnchor()

    result = verifier.verify(
        output=output,
        commitment=commitment_bytes,
        model_id=model,
        params=params_dict if model else None,
        prompt=prompt,
        anchor_tx=anchor_tx,
        anchor_backend=anchor_backend,
    )

    if result.valid:
        console.print("[green]✓ Verification PASSED[/green]")
    else:
        console.print("[red]✗ Verification FAILED[/red]")

    for check in result.checks_passed:
        console.print(f"  [green]✓ {check}[/green]")
    for check in result.checks_failed:
        console.print(f"  [red]✗ {check}[/red]")
    if result.details:
        for k, v in result.details.items():
            console.print(f"  {k}: {v}")


@main.command()
@click.option("--log", "log_path", default=None, help="Log file path")
def status(log_path):
    """Show log statistics."""
    log = TamperEvidentLog(Path(log_path) if log_path else None)

    table = Table(title="Veritas Log Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Log Path", str(log.log_path))
    table.add_row("Entries", str(log.count))

    if log.count > 0:
        root = log.get_merkle_root()
        table.add_row("Merkle Root", root.hex())
        entries = log.get_entries()
        models = set(e.get("model_id", "?") for e in entries)
        table.add_row("Models", ", ".join(models))

    console.print(table)


if __name__ == "__main__":
    main()
