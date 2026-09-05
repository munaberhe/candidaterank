import typer
import pandas as pd
from pathlib import Path
from typing import Optional

from .scoring import rank_genes

app = typer.Typer(help="CandidateRank CLI")

@app.command()
def rank(
    input: Path = typer.Argument(..., help="Input CSV/TSV with gene, effect, pval, [direction]"),
    output: Path = typer.Argument(..., help="Output CSV path"),
    assay: str = typer.Option("wgbs", help="Assay type: wgbs, rnaseq, vcf"),
    tissues: str = typer.Option("spinal_cord", help="Comma-separated tissues, e.g. spinal_cord,motor_neuron"),
    pathways: str = typer.Option("neurodegeneration", help="Comma-separated pathways"),
    traits: str = typer.Option("SMA", help="Comma-separated GWAS/OMIM traits"),
    weights: str = typer.Option("expr=0.4,pathway=0.3,gwas=0.2,effect=0.1", help="Weights as key=value pairs"),
    filter_direction: Optional[str] = typer.Option(None, help="Filter by direction: hyper or hypo"),
    filter_min_abs_effect: Optional[float] = typer.Option(None, help="Min |effect|"),
    filter_max_pval: Optional[float] = typer.Option(None, help="Max p-value/FDR"),
):
    # Parse inputs
    df = pd.read_csv(input)
    context = {
        "tissues": [t.strip() for t in tissues.split(",")],
        "pathways": [p.strip() for p in pathways.split(",")],
        "traits": [t.strip() for t in traits.split(",")],
    }
    w = {}
    for pair in weights.split(","):
        k, v = pair.split("=")
        w[k.strip()] = float(v.strip())

    filters = {
        "direction": filter_direction,
        "min_abs_effect": filter_min_abs_effect,
        "max_pval": filter_max_pval,
    }

    ranked = rank_genes(df, assay=assay, context=context, weights=w, filters=filters)
    ranked.to_csv(output, index=False)
    typer.echo(f"Ranked {len(ranked)} genes → {output}")

@app.command()
def explain(
    input: Path = typer.Argument(..., help="Input CSV/TSV"),
    gene: str = typer.Argument(..., help="Gene symbol to explain"),
    tissues: str = typer.Option("spinal_cord", help="Comma-separated tissues"),
    pathways: str = typer.Option("neurodegeneration", help="Comma-separated pathways"),
    traits: str = typer.Option("SMA", help="Comma-separated traits"),
):
    df = pd.read_csv(input)
    row = df[df["gene"].str.lower() == gene.lower()]
    if row.empty:
        typer.echo(f"Gene {gene} not found in input.")
        raise typer.Exit(1)
    # For v1, just print basic info
    typer.echo(f"Gene: {row['gene'].iloc[0]}")
    typer.echo(f"Effect: {row['effect'].iloc[0]}")
    typer.echo(f"P-value: {row['pval'].iloc[0]}")
    typer.echo("Detailed score breakdown coming in v2.")

if __name__ == "__main__":
    app()