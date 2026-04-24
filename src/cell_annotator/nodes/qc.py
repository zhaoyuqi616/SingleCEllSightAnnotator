from __future__ import annotations
from ..state import AnnotationState
from ..utils.qc import qc_flags_for_markers


def cluster_qc(state: AnnotationState) -> AnnotationState:
    results = state.get("per_cluster_results", {})

    for cluster, markers in state["normalized_cluster_to_markers"].items():
        flags = qc_flags_for_markers(markers)
        results[cluster] = {
            "cluster_id": cluster,
            "raw_markers": state["cluster_to_markers"][cluster],
            "normalized_markers": markers,
            "qc_flags": flags,
            "review_required": bool(flags and ("possible_doublet" in flags)),
        }

    logs = state.get("logs", [])
    logs.append("Computed cluster QC flags")

    state["per_cluster_results"] = results
    state["logs"] = logs
    return state
