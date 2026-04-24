from __future__ import annotations
import uuid
from collections import defaultdict
from ..state import AnnotationState
from ..utils.io import load_marker_table, detect_input_format


def ingest_input(state: AnnotationState) -> AnnotationState:
    path = state["input_path"]
    df = load_marker_table(path)
    input_format = detect_input_format(df)

    cluster_to_markers = defaultdict(list)
    df.columns = [c.lower() for c in df.columns]

    for _, row in df.iterrows():
        cluster = str(row["cluster"])
        gene = str(row["gene"])
        cluster_to_markers[cluster].append(gene)

    logs = state.get("logs", [])
    logs.append(f"Ingested {len(df)} rows from {path}")
    logs.append(f"Detected input format: {input_format}")

    state["run_id"] = str(uuid.uuid4())
    state["input_format"] = input_format
    state["cluster_to_markers"] = dict(cluster_to_markers)
    state["logs"] = logs
    return state
