from __future__ import annotations
import pandas as pd


def detect_input_format(df: pd.DataFrame) -> str:
    cols = {c.lower() for c in df.columns}

    if {"cluster", "gene"}.issubset(cols):
        if "avg_log2fc" in cols:
            return "findallmarkers"
        return "simple_cluster_gene"

    raise ValueError(
        "Unable to detect input format. Expected either [cluster, gene] "
        "or a FindAllMarkers-like table."
    )


def load_marker_table(path: str) -> pd.DataFrame:
    if path.endswith(".csv"):
        return pd.read_csv(path)
    return pd.read_csv(path, sep="\t")
