import pandas as pd
import numpy as np

from .data_loaders import load_expression_data, load_pathway_data, load_gwas_data

def score_expression(genes: pd.Series, tissues: list[str]) -> pd.Series:
    expr = load_expression_data()
    # Filter to requested tissues
    expr = expr[expr["tissue"].isin(tissues)]
    # Aggregate per gene (mean across tissues)
    expr_gene = expr.groupby("gene")["expr_value"].mean().reset_index()
    expr_gene.columns = ["gene", "expr_mean"]
    # Merge
    df = pd.DataFrame({"gene": genes})
    df = df.merge(expr_gene, on="gene", how="left")
    df["expr_mean"] = df["expr_mean"].fillna(0)
    # Normalize to 0–1 (simple min-max)
    min_v, max_v = df["expr_mean"].min(), df["expr_mean"].max()
    if max_v - min_v == 0:
        df["S_expr"] = 0.0
    else:
        df["S_expr"] = (df["expr_mean"] - min_v) / (max_v - min_v)
    return df["S_expr"]

def score_pathway(genes: pd.Series, pathways: list[str]) -> pd.Series:
    pw = load_pathway_data()
    pw = pw[pw["pathway"].isin(pathways)]
    in_pathway = pw["gene"].unique()
    S = genes.isin(in_pathway).astype(float)
    return S

def score_gwas(genes: pd.Series, traits: list[str]) -> pd.Series:
    gw = load_gwas_data()
    gw = gw[gw["trait"].isin(traits)]
    in_gwas = gw["gene"].unique()
    S = genes.isin(in_gwas).astype(float)
    return S

def score_effect(df: pd.DataFrame) -> pd.Series:
    """
    Normalize absolute effect size to 0–1.
    """
    eff = df["effect"].abs()
    min_v, max_v = eff.min(), eff.max()
    if max_v - min_v == 0:
        return pd.Series(0.0, index=df.index)
    return (eff - min_v) / (max_v - min_v)

def compute_total_score(
    df: pd.DataFrame,
    weights: dict,
    context: dict,
) -> pd.DataFrame:
    """
    Add score columns and total_score to df.
    """
    df = df.copy()

    S_expr = score_expression(df["gene"], context["tissues"])
    S_pathway = score_pathway(df["gene"], context["pathways"])
    S_gwas = score_gwas(df["gene"], context["traits"])
    S_effect = score_effect(df)

    df["S_expr"] = S_expr.values
    df["S_pathway"] = S_pathway.values
    df["S_gwas"] = S_gwas.values
    df["S_effect"] = S_effect.values

    # Normalize weights
    total_w = sum(weights.values())
    w = {k: v / total_w for k, v in weights.items()}

    df["total_score"] = (
        w["expr"] * df["S_expr"] +
        w["pathway"] * df["S_pathway"] +
        w["gwas"] * df["S_gwas"] +
        w["effect"] * df["S_effect"]
    )

    df = df.sort_values("total_score", ascending=False).reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)
    return df