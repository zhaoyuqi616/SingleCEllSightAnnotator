from __future__ import annotations
from ..state import AnnotationState
from ..config import settings
from ..utils.scoring import assign_confidence_band


def score_candidates(state: AnnotationState) -> AnnotationState:
    review_queue = state.get("review_queue", [])

    for cluster, result in state["per_cluster_results"].items():
        candidates = result.get("candidate_scores", [])
        confidence, band = assign_confidence_band(
            candidates,
            high_threshold=settings.high_confidence_threshold,
            moderate_threshold=settings.moderate_confidence_threshold,
            min_gap_high=settings.min_score_gap_high,
            min_gap_moderate=settings.min_score_gap_moderate,
        )

        result["confidence"] = confidence
        result["confidence_band"] = band

        if band == "low" or "possible_doublet" in result.get("qc_flags", []):
            result["review_required"] = True
            review_queue.append(cluster)

    state["review_queue"] = sorted(set(review_queue))
    logs = state.get("logs", [])
    logs.append("Assigned confidence bands")
    state["logs"] = logs
    return state


def ambiguity_router(state: AnnotationState) -> str:
    for result in state["per_cluster_results"].values():
        if result.get("confidence_band") in {"moderate", "low"}:
            return "llm"
    return "finalize"
