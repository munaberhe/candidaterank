import pandas as pd

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply user-specified filters to the input DataFrame.

    Supported filters:
      - direction: "hyper" | "hypo" | None
      - min_abs_effect: float | None
      - max_pval: float | None
    """
    df = df.copy()

    if filters.get("direction") is not None:
        direction = filters["direction"]
        # If no direction column, infer from effect sign
        if "direction" not in df.columns:
            df["direction"] = df["effect"].apply(lambda x: "hyper" if x >= 0 else "hypo")
        df = df[df["direction"] == direction]

    if filters.get("min_abs_effect") is not None:
        min_val = filters["min_abs_effect"]
        df = df[df["effect"].abs() >= min_val]

    if filters.get("max_pval") is not None:
        max_val = filters["max_pval"]
        df = df[df["pval"] <= max_val]

    return df