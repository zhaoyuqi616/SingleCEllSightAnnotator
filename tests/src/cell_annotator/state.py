from __future__ import annotations
from typing import TypedDict, Dict, List, Optional, Any


class CandidateScore(TypedDict, total=False):
    cell_type: str
    score: float
    matched_markers: List[str]
    missing_markers: List[str]
    conflicting_markers: List[str]
    explanation: str


class ClusterResult(TypedDict, total=False):
    cluster_id: str
    raw_markers: List[str]
    normalized_markers: List[str]
    qc_flags: List[str]
    candidate_scores: List[CandidateScore]
    selected_label: Optional[str]
    confidence: Optional[float]
    confidence_band: Optional[str]
    matched_markers: List[str]
    missing_expected_markers: List[str]
    conflicting_markers: List[str]
    rationale: Optional[str]
    alternatives: List[Dict[str, Any]]
    review_required: bool
    review_notes: Optional[str]


class AnnotationState(TypedDict, total=False):
    run_id: str
    input_path: str
    input_format: str
    species: str
    tissue: Optional[str]
    disease_context: Optional[str]
    cluster_to_markers: Dict[str, List[str]]
    normalized_cluster_to_markers: Dict[str, List[str]]
    unmapped_genes: List[str]
    global_qc_flags: List[str]
    per_cluster_results: Dict[str, ClusterResult]
    review_queue: List[str]
    final_output_path: Optional[str]
    logs: List[str]
