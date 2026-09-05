import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add repo root to path so we can import candidaterank
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from candidaterank.scoring import rank_genes

st.set_page_config(page_title="CandidateRank", layout="wide")
st.title("CandidateRank")

st.markdown("""
Upload your gene-level results (DMR-associated genes, DEGs, etc.) and get an
explainable, prioritized ranking.
""")

uploaded = st.file_uploader("CSV file", type=["csv"])

if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.write("Preview of your data:", df.head())

    assay = st.selectbox("Assay", ["wgbs", "rnaseq", "vcf"])
    tissues = st.text_input("Tissues (comma-separated)", "spinal_cord")
    pathways = st.text_input("Pathways (comma-separated)", "neurodegeneration")
    traits = st.text_input("Traits (comma-separated)", "SMA")

    w_expr = st.slider("Weight: expression", 0.0, 1.0, 0.4, 0.05)
    w_pathway = st.slider("Weight: pathway", 0.0, 1.0, 0.3, 0.05)
    w_gwas = st.slider("Weight: GWAS/OMIM", 0.0, 1.0, 0.2, 0.05)
    w_effect = st.slider("Weight: effect size", 0.0, 1.0, 0.1, 0.05)

    weights = {
        "expr": w_expr,
        "pathway": w_pathway,
        "gwas": w_gwas,
        "effect": w_effect,
    }

    filter_direction = st.selectbox("Filter by direction", [None, "hyper", "hypo"])
    filter_min_abs_effect = st.number_input("Min |effect|", min_value=0.0, value=0.0)
    filter_max_pval = st.number_input("Max p-value/FDR", min_value=0.0, value=1.0)

    filters = {
        "direction": filter_direction if filter_direction else None,
        "min_abs_effect": filter_min_abs_effect if filter_min_abs_effect > 0 else None,
        "max_pval": filter_max_pval if filter_max_pval > 0 else None,
    }

    if st.button("Rank candidates"):
        context = {
            "tissues": [t.strip() for t in tissues.split(",")],
            "pathways": [p.strip() for p in pathways.split(",")],
            "traits": [t.strip() for t in traits.split(",")],
        }
        ranked = rank_genes(df, assay=assay, context=context, weights=weights, filters=filters)
        st.write("Ranked results:")
        st.dataframe(ranked)

        csv = ranked.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download ranked CSV",
            csv,
            "ranked_genes.csv",
            "text/csv",
            key="download-csv"
        )
        