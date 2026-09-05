import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def load_expression_data() -> pd.DataFrame:
    """
    Return a DataFrame: gene, tissue, expr_value.
    For v1, use toy data.
    """
    data = {
        "gene": ["SMN1", "ATP2A1", "CHCHD10", "NEFL", "SOD1"],
        "tissue": ["spinal_cord"] * 5,
        "expr_value": [8.0, 6.5, 5.0, 7.0, 6.0],
    }
    return pd.DataFrame(data)

def load_pathway_data() -> pd.DataFrame:
    """
    Return a DataFrame: gene, pathway.
    """
    data = {
        "gene": ["SMN1", "ATP2A1", "SOD1", "NEFL"],
        "pathway": ["neurodegeneration"] * 4,
    }
    return pd.DataFrame(data)

def load_gwas_data() -> pd.DataFrame:
    """
    Return a DataFrame: gene, trait.
    """
    data = {
        "gene": ["SMN1", "SOD1"],
        "trait": ["SMA"],
    }
    return pd.DataFrame(data)