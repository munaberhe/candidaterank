# CandidateRank — Vision

CandidateRank helps researchers go from large omics result tables (DMR-associated genes, DEGs, variant-level gene summaries) to a short, explainable list of candidate genes for follow-up.

## v1 scope

- Input: CSV/TSV with at least: gene, effect size, p-value/FDR, optional direction.
- Evidence:
  - Tissue expression (e.g., spinal cord, motor neuron).
  - Pathway membership (e.g., neurodegeneration pathways).
  - GWAS/OMIM disease links (curated set).
- Features:
  - Filter by direction (hypo/hyper), effect size, significance.
  - Configure evidence weights.
  - Transparent scoring: see why each gene is ranked high.
  - CLI and web (Streamlit) interfaces.
  - Dockerized deployment.

## Out of scope for v1

- No complex ML models.
- No user accounts.
- No arbitrary custom gene sets (v2).
- No heavy data management (small CSVs only).