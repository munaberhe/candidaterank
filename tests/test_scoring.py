import pandas as pd
from candidaterank.scoring import rank_genes

def test_rank_genes_basic():
    df = pd.DataFrame({
        "gene": ["SMN1", "ATP2A1", "CHCHD10"],
        "effect": [0.22, 0.15, -0.18],
        "pval": [1e-6, 3e-4, 2e-3],
        "direction": ["hyper", "hyper", "hypo"],
    })
    context = {
        "tissues": ["spinal_cord"],
        "pathways": ["neurodegeneration"],
        "traits": ["SMA"],
    }
    weights = {"expr": 0.4, "pathway": 0.3, "gwas": 0.2, "effect": 0.1}
    filters = {"direction": "hyper", "min_abs_effect": 0.1, "max_pval": 0.01}

    ranked = rank_genes(df, assay="wgbs", context=context, weights=weights, filters=filters)
    assert len(ranked) > 0
    assert "total_score" in ranked.columns
    assert "rank" in ranked.columns