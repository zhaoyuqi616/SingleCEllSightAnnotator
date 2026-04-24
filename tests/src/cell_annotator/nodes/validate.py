from __future__ import annotations
from ..state import AnnotationState


def validate_schema(state: AnnotationState) -> AnnotationState:
    if "cluster_to_markers" not in state or not state["cluster_to_markers"]:
        raise ValueError("No cluster_to_markers found after ingestion.")

    for cluster, markers in state["cluster_to_markers"].items():
        if not cluster:
            raise ValueError("Empty cluster ID found.")
        if not markers:
            raise ValueError(f"No markers found for cluster {cluster}")

    logs = state.get("logs", [])
    logs.append(f"Validated {len(state['cluster_to_markers'])} clusters")
    state["logs"] = logs
    return state
