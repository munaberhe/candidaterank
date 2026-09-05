# Input format

CandidateRank accepts a CSV or TSV with at least the following columns:

- `gene` (required): gene symbol or Ensembl ID.
- `effect` (required): numeric effect size.
  - For WGBS: mean Δmeth per gene.
  - For RNA-seq: log2FC.
  - For variants: gene-level score (e.g., CADD, burden).
- `pval` (required): p-value or FDR.
- `direction` (optional): "hyper", "hypo", "up", "down".
  - If missing, direction is inferred from sign of `effect`.

Optional columns:

- `chr`, `start`, `end`: genomic coordinates.
- `gene_biotype`: e.g., "protein_coding".

Example (CSV):

```csv
gene,effect,pval,direction
SMN1,0.22,1e-6,hyper
ATP2A1,0.15,3e-4,hyper
CHCHD10,-0.18,2e-3,hypo
```