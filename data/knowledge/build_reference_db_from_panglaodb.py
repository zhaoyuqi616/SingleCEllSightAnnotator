#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd


def normalize_species_field(raw_species: str) -> List[str]:
    """
    PanglaoDB species column uses values like:
      'Hs'       -> human
      'Mm'       -> mouse
      'Mm Hs'    -> both
    """
    if pd.isna(raw_species):
        return []

    raw_species = str(raw_species).strip()
    species_list = []

    if "Hs" in raw_species:
        species_list.append("human")
    if "Mm" in raw_species:
        species_list.append("mouse")

    return species_list


def clean_gene_symbol(gene: str) -> str:
    if pd.isna(gene):
        return ""
    return str(gene).strip().upper()


def score_markers(
    df_subset: pd.DataFrame,
    target_species: str,
) -> pd.DataFrame:
    """
    Compute a ranking score for markers within each cell type.

    Heuristic:
    - prefer canonical markers
    - prefer higher specificity
    - prefer higher sensitivity
    - slightly penalize ubiquitous markers
    """
    df_subset = df_subset.copy()

    if target_species == "human":
        sens_col = "sensitivity_human"
        spec_col = "specificity_human"
    elif target_species == "mouse":
        sens_col = "sensitivity_mouse"
        spec_col = "specificity_mouse"
    else:
        raise ValueError("target_species must be 'human' or 'mouse'")

    # Fill missing values safely
    for col in [sens_col, spec_col, "ubiquitousness index", "canonical marker"]:
        if col not in df_subset.columns:
            df_subset[col] = 0.0
        df_subset[col] = pd.to_numeric(df_subset[col], errors="coerce").fillna(0.0)

    # Weighted score
    # canonical markers get a strong boost
    df_subset["marker_score"] = (
        3.0 * df_subset["canonical marker"]
        + 2.0 * df_subset[spec_col]
        + 1.0 * df_subset[sens_col]
        - 0.5 * df_subset["ubiquitousness index"]
    )

    return df_subset.sort_values(
        by=["marker_score", "canonical marker", spec_col, sens_col],
        ascending=[False, False, False, False],
    )


def build_reference_db(
    panglao_tsv: str,
    output_json: str,
    target_species: str = "human",
    organ_filter: str | None = None,
    min_specificity: float = 0.0,
    min_sensitivity: float = 0.0,
    top_positive: int = 8,
    top_supporting: int = 6,
    min_markers_per_cell_type: int = 2,
) -> List[Dict[str, Any]]:
    """
    Build a JSON reference DB for the agent from PanglaoDB markers.

    Output schema:
    [
      {
        "cell_type": ...,
        "species": "human"|"mouse",
        "positive_markers": [...],
        "supporting_markers": [...],
        "negative_markers": []
      }
    ]
    """

    df = pd.read_csv(panglao_tsv, sep="\t")

    required_cols = [
        "species",
        "official gene symbol",
        "cell type",
        "canonical marker",
        "ubiquitousness index",
        "organ",
        "sensitivity_human",
        "sensitivity_mouse",
        "specificity_human",
        "specificity_mouse",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in PanglaoDB file: {missing}")

    # Clean
    df["official gene symbol"] = df["official gene symbol"].map(clean_gene_symbol)
    df = df[df["official gene symbol"] != ""].copy()
    df["cell type"] = df["cell type"].astype(str).str.strip()
    df["organ"] = df["organ"].astype(str).str.strip()

    # Expand species to normalized list
    df["normalized_species"] = df["species"].map(normalize_species_field)

    # Keep only rows relevant to target species
    df = df[df["normalized_species"].map(lambda xs: target_species in xs)].copy()

    if organ_filter:
        organ_filter_lower = organ_filter.strip().lower()
        df = df[df["organ"].str.lower() == organ_filter_lower].copy()

    # Apply species-specific thresholds
    if target_species == "human":
        spec_col = "specificity_human"
        sens_col = "sensitivity_human"
    elif target_species == "mouse":
        spec_col = "specificity_mouse"
        sens_col = "sensitivity_mouse"
    else:
        raise ValueError("target_species must be 'human' or 'mouse'")

    df[spec_col] = pd.to_numeric(df[spec_col], errors="coerce").fillna(0.0)
    df[sens_col] = pd.to_numeric(df[sens_col], errors="coerce").fillna(0.0)

    df = df[
        (df[spec_col] >= min_specificity) &
        (df[sens_col] >= min_sensitivity)
    ].copy()

    reference_db: List[Dict[str, Any]] = []

    # Build one record per cell type
    for cell_type, group in df.groupby("cell type"):
        ranked = score_markers(group, target_species=target_species)

        # Drop duplicate genes within the same cell type
        ranked = ranked.drop_duplicates(subset=["official gene symbol"], keep="first")

        if ranked.empty:
            continue

        # positive markers:
        # prefer canonical markers first, then highest-scoring others
        canonical_genes = ranked.loc[
            ranked["canonical marker"] >= 1, "official gene symbol"
        ].tolist()

        noncanonical_genes = ranked.loc[
            ranked["canonical marker"] < 1, "official gene symbol"
        ].tolist()

        positive_markers = []
        for gene in canonical_genes + noncanonical_genes:
            if gene not in positive_markers:
                positive_markers.append(gene)
            if len(positive_markers) >= top_positive:
                break

        # supporting markers:
        # take next best genes not already used as positive
        supporting_markers = []
        for gene in ranked["official gene symbol"].tolist():
            if gene not in positive_markers and gene not in supporting_markers:
                supporting_markers.append(gene)
            if len(supporting_markers) >= top_supporting:
                break

        if len(positive_markers) < min_markers_per_cell_type:
            continue

        record = {
            "cell_type": cell_type,
            "species": target_species,
            "positive_markers": positive_markers,
            "supporting_markers": supporting_markers,
            "negative_markers": []
        }

        # Optional metadata: useful for future V2, harmless if your current agent ignores it
        if organ_filter:
            record["organ"] = organ_filter

        reference_db.append(record)

    # Sort for stable output
    reference_db = sorted(reference_db, key=lambda x: x["cell_type"].lower())

    output_path = Path(output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(reference_db, f, indent=2)

    return reference_db


def main():
    parser = argparse.ArgumentParser(
        description="Build a cell annotation reference DB JSON from PanglaoDB TSV."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to PanglaoDB_markers_27_Mar_2020.tsv"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON path"
    )
    parser.add_argument(
        "--species",
        default="human",
        choices=["human", "mouse"],
        help="Target species for reference DB"
    )
    parser.add_argument(
        "--organ",
        default=None,
        help="Optional organ filter, e.g. 'Pancreas', 'Lung', 'Immune system'"
    )
    parser.add_argument(
        "--min-specificity",
        type=float,
        default=0.0,
        help="Minimum specificity threshold"
    )
    parser.add_argument(
        "--min-sensitivity",
        type=float,
        default=0.0,
        help="Minimum sensitivity threshold"
    )
    parser.add_argument(
        "--top-positive",
        type=int,
        default=8,
        help="Number of positive markers per cell type"
    )
    parser.add_argument(
        "--top-supporting",
        type=int,
        default=6,
        help="Number of supporting markers per cell type"
    )
    parser.add_argument(
        "--min-markers-per-cell-type",
        type=int,
        default=2,
        help="Minimum positive markers required to keep a cell type"
    )

    args = parser.parse_args()

    reference_db = build_reference_db(
        panglao_tsv=args.input,
        output_json=args.output,
        target_species=args.species,
        organ_filter=args.organ,
        min_specificity=args.min_specificity,
        min_sensitivity=args.min_sensitivity,
        top_positive=args.top_positive,
        top_supporting=args.top_supporting,
        min_markers_per_cell_type=args.min_markers_per_cell_type,
    )

    print(f"Built {len(reference_db)} reference entries")
    print(f"Saved to: {args.output}")


if __name__ == "__main__":
    main()
