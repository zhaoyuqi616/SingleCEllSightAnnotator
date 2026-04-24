from __future__ import annotations
from ..state import AnnotationState


def finalize_annotation(state: AnnotationState) -> AnnotationState:
    for cluster, result in state["per_cluster_results"].items():
        if result.get("selected_label"):
            continue

        candidates = result.get("candidate_scores", [])
        if candidates:
            top = candidates[0]
            result["selected_label"] = top["cell_type"]
            result["matched_markers"] = top.get("matched_markers", [])
            result["missing_expected_markers"] = top.get("missing_markers", [])
            result["conflicting_markers"] = top.get("conflicting_markers", [])
            result["rationale"] = (
                f"Top structured candidate based on marker overlap. {top.get('explanation', '')}"
            )
            result["alternatives"] = [
                {"label": c["cell_type"], "reason": f"score={c['score']}"}
                for c in candidates[1:3]
            ]
        else:
            result["selected_label"] = "Unknown"
            result["rationale"] = "No supported candidate found from structured marker database."
            result["review_required"] = True

    logs = state.get("logs", [])
    logs.append("Finalized annotations")
    state["logs"] = logs
    return state
