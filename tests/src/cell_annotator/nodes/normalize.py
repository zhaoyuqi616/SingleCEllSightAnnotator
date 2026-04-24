from __future__ import annotations
from ..state import AnnotationState
from ..utils.gene_normalization import normalize_gene_list


def normalize_genes(state: AnnotationState) -> AnnotationState:
    normalized_cluster_to_markers = {}
    unmapped_all = []

    for cluster, genes in state["cluster_to_markers"].items():
        normalized, unmapped = normalize_gene_list(genes)
        normalized_cluster_to_markers[cluster] = normalized
        unmapped_all.extend(unmapped)

    logs = state.get("logs", [])
    logs.append("Normalized gene symbols")

    state["normalized_cluster_to_markers"] = normalized_cluster_to_markers
    state["unmapped_genes"] = unmapped_all
    state["logs"] = logs
    return state
