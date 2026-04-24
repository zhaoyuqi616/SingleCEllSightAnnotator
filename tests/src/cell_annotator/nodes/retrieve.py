from __future__ import annotations
from ..state import AnnotationState
from ..knowledge.marker_db import load_marker_db
from ..config import settings
from ..utils.scoring import rank_candidates


def retrieve_structured_candidates(state: AnnotationState) -> AnnotationState:
    marker_db = load_marker_db(settings.curated_marker_db)

    for cluster, markers in state["normalized_cluster_to_markers"].items():
        ranked = rank_candidates(
            query_markers=markers,
            marker_db=marker_db,
            species=state.get("species", settings.species_default),
            top_k=settings.top_k_candidates,
        )
        state["per_cluster_results"][cluster]["candidate_scores"] = ranked

    logs = state.get("logs", [])
    logs.append("Retrieved and ranked structured cell-type candidates")
    state["logs"] = logs
    return state
