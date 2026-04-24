from __future__ import annotations
from ..state import AnnotationState


def human_review(state: AnnotationState) -> AnnotationState:
    for cluster in state.get("review_queue", []):
        result = state["per_cluster_results"][cluster]
        if result.get("review_required", False):
            note = result.get("review_notes") or ""
            result["review_notes"] = (note + " | Human review recommended").strip(" |")

    logs = state.get("logs", [])
    logs.append("Marked review-required clusters")
    state["logs"] = logs
    return state
