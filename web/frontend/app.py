import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from candidaterank.scoring import rank_genes


st.set_page_config(
    page_title="CandidateRank",
    layout="wide",
)

st.title("CandidateRank")

st.markdown(
    """
Upload your gene-level results—such as DMR-associated genes, DEGs, or
variant-level gene summaries—and generate an explainable candidate ranking.
"""
)

uploaded = st.file_uploader(
    "CSV file",
    type=["csv"],
)

if uploaded is None:
    st.info(
        "Upload a CSV containing at least `gene`, `effect`, and `pval` columns "
        "to begin."
    )
    st.stop()

try:
    df = pd.read_csv(uploaded)
except Exception as error:
    st.error(f"Could not read the uploaded CSV file: {error}")
    st.stop()

required_columns = {"gene", "effect", "pval"}
missing_columns = required_columns - set(df.columns)

if missing_columns:
    st.error(
        "Your CSV is missing required column(s): "
        f"`{', '.join(sorted(missing_columns))}`. "
        "Required columns are: `gene`, `effect`, and `pval`."
    )
    st.stop()

st.subheader("Input preview")
st.dataframe(
    df.head(),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Ranking configuration")

assay = st.selectbox(
    "Assay type",
    ["wgbs", "rnaseq", "vcf"],
    help=(
        "WGBS uses methylation effects, RNA-seq uses log fold changes, "
        "and VCF supports future gene-level variant prioritization."
    ),
)

tissues = st.text_input(
    "Tissues (comma-separated)",
    "spinal_cord",
    help="For example: spinal_cord,motor_neuron,brain.",
)

pathways = st.text_input(
    "Pathways (comma-separated)",
    "neurodegeneration",
    help="For example: neurodegeneration,synaptic_function.",
)

traits = st.text_input(
    "Traits or diseases (comma-separated)",
    "SMA",
    help="For example: SMA,ALS,neuropathy.",
)

st.subheader("Evidence weights")

st.caption(
    "Weights are normalized automatically. Set an evidence source to 0 if "
    "you do not want it to influence the ranking."
)

weight_col1, weight_col2 = st.columns(2)

with weight_col1:
    w_expr = st.slider(
        "Weight: expression evidence",
        min_value=0.0,
        max_value=1.0,
        value=0.4,
        step=0.05,
    )

    w_pathway = st.slider(
        "Weight: pathway membership",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05,
    )

with weight_col2:
    w_gwas = st.slider(
        "Weight: disease evidence",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        help=(
            "The MVP currently uses a curated toy gene-trait table. "
            "Real GWAS and disease-resource integration will be added later."
        ),
    )

    w_effect = st.slider(
        "Weight: effect size",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.05,
    )

weights = {
    "expr": w_expr,
    "pathway": w_pathway,
    "gwas": w_gwas,
    "effect": w_effect,
}

if sum(weights.values()) == 0:
    st.warning("Choose a weight greater than 0 for at least one evidence source.")

st.subheader("Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    filter_direction = st.selectbox(
        "Filter by direction",
        options=["all", "hyper", "hypo"],
        help=(
            "For WGBS, use hyper or hypo. If your input has no direction "
            "column, CandidateRank infers direction from the sign of effect."
        ),
    )

with filter_col2:
    filter_min_abs_effect = st.number_input(
        "Minimum |effect|",
        min_value=0.0,
        value=0.0,
        step=0.01,
    )

with filter_col3:
    filter_max_pval = st.number_input(
        "Maximum p-value/FDR",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.01,
        format="%.4f",
    )

filters = {
    "direction": None if filter_direction == "all" else filter_direction,
    "min_abs_effect": (
        filter_min_abs_effect if filter_min_abs_effect > 0 else None
    ),
    "max_pval": filter_max_pval if filter_max_pval > 0 else None,
}

if st.button(
    "Rank candidates",
    type="primary",
    disabled=sum(weights.values()) == 0,
):
    context = {
        "tissues": [item.strip() for item in tissues.split(",") if item.strip()],
        "pathways": [
            item.strip() for item in pathways.split(",") if item.strip()
        ],
        "traits": [item.strip() for item in traits.split(",") if item.strip()],
    }

    try:
        ranked = rank_genes(
            df,
            assay=assay,
            context=context,
            weights=weights,
            filters=filters,
        )
    except Exception as error:
        st.error(f"Candidate ranking failed: {error}")
        st.stop()

    st.session_state["ranked"] = ranked
    st.session_state["context"] = context
    st.session_state["weights"] = weights
    st.session_state["assay"] = assay

if "ranked" not in st.session_state:
    st.stop()

ranked = st.session_state["ranked"]
context = st.session_state["context"]
saved_weights = st.session_state["weights"]

if ranked.empty:
    st.warning(
        "No genes passed the selected filters. Try one or more of the following:"
    )
    st.markdown(
        "- Select `all` instead of `hyper` or `hypo`\n"
        "- Lower the minimum absolute effect threshold\n"
        "- Increase the maximum p-value/FDR threshold"
    )
    st.stop()

st.subheader("Ranked results")

display_names = {
    "S_expr": "Expression score",
    "S_pathway": "Pathway score",
    "S_gwas": "Disease evidence score",
    "S_effect": "Effect-size score",
    "total_score": "Priority score",
    "rank": "Rank",
}

ranked_display = ranked.rename(columns=display_names)

st.dataframe(
    ranked_display,
    use_container_width=True,
    hide_index=True,
)

st.subheader("Explain a candidate")

selected_gene = st.selectbox(
    "Choose a gene",
    ranked["gene"].tolist(),
    key="candidate_gene_selector",
)

selected = ranked.loc[
    ranked["gene"] == selected_gene
].iloc[0]

st.markdown(f"### {selected['gene']}")

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

metric_col1.metric(
    "Priority score",
    f"{selected['total_score']:.3f}",
)

metric_col2.metric(
    "Rank",
    int(selected["rank"]),
)

metric_col3.metric(
    "Expression",
    f"{selected['S_expr']:.3f}",
)

metric_col4.metric(
    "Pathway",
    f"{selected['S_pathway']:.3f}",
)

metric_col5.metric(
    "Disease evidence",
    f"{selected['S_gwas']:.3f}",
)

st.markdown("#### Score breakdown")

component_rows = pd.DataFrame(
    {
        "Evidence source": [
            "Expression",
            "Pathway membership",
            "Disease evidence",
            "Effect size",
        ],
        "Component score": [
            selected["S_expr"],
            selected["S_pathway"],
            selected["S_gwas"],
            selected["S_effect"],
        ],
        "User weight": [
            saved_weights["expr"],
            saved_weights["pathway"],
            saved_weights["gwas"],
            saved_weights["effect"],
        ],
    }
)

component_rows["Weighted contribution"] = (
    component_rows["Component score"] * component_rows["User weight"]
)

st.dataframe(
    component_rows.style.format(
        {
            "Component score": "{:.3f}",
            "User weight": "{:.2f}",
            "Weighted contribution": "{:.3f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.markdown("#### Why this candidate ranked here")

reasons = []

if selected["S_expr"] > 0:
    reasons.append(
        "Has expression evidence in the selected tissue context: "
        f"`{', '.join(context['tissues'])}`."
    )

if selected["S_pathway"] > 0:
    reasons.append(
        "Matches one or more selected pathway sets: "
        f"`{', '.join(context['pathways'])}`."
    )

if selected["S_gwas"] > 0:
    reasons.append(
        "Has curated disease or trait evidence for: "
        f"`{', '.join(context['traits'])}`."
    )

if selected["S_effect"] > 0:
    reasons.append(
        "Has a relatively strong absolute effect size in the uploaded result "
        f"table: `{selected['effect']}`."
    )

if reasons:
    for reason in reasons:
        st.write(f"- {reason}")
else:
    st.info(
        "This candidate is ranked primarily from its relative effect-size "
        "evidence under the current settings."
    )

st.caption(
    "CandidateRank is an evidence-prioritization aid, not a causal-inference "
    "tool. Interpret ranked genes using the original study design, underlying "
    "data, and relevant biological literature."
)

csv = ranked.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download ranked CSV",
    csv,
    "ranked_genes.csv",
    "text/csv",
    key="download-ranked-csv",
)