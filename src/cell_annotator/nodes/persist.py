from __future__ import annotations
from pathlib import Path
import pandas as pd
from ..state import AnnotationState
from ..config import settings


def persist_outputs(state: AnnotationState) -> AnnotationState:
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)

    records = []
    for cluster, result in state["per_cluster_results"].items():
        records.append({
            "Cluster": cluster,
            "Cell_Type": result.get("selected_label"),
            "Confidence": result.get("confidence"),
            "QC": ";".join(result.get("qc_flags", [])),
            "Review": result.get("review_required"),
            "Rationale": result.get("rationale"),
            "Top Markers": ";".join(result.get("matched_markers", [])),
        })

    df = pd.DataFrame(records)
    out_path = Path(settings.output_dir) / f"{state['run_id']}_annotation_results.csv"
    df.to_csv(out_path, index=False)

    state["final_output_path"] = str(out_path)
    logs = state.get("logs", [])
    logs.append(f"Saved final output to {out_path}")
    state["logs"] = logs
    return state
