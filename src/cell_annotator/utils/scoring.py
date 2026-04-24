from __future__ import annotations
from typing import Dict, Any, List


def score_candidate(
    query_markers: List[str],
    candidate: Dict[str, Any],
) -> Dict[str, Any]:
    qset = set(query_markers)
    pos = set(candidate.get("positive_markers", []))
    supp = set(candidate.get("supporting_markers", []))
    neg = set(candidate.get("negative_markers", []))

    matched_pos = sorted(qset & pos)
    matched_supp = sorted(qset & supp)
    conflicting = sorted(qset & neg)
    missing_pos = sorted(pos - qset)

    pos_score = len(matched_pos) / max(len(pos), 1)
    supp_score = 0.5 * len(matched_supp) / max(len(supp), 1) if supp else 0.0
    neg_penalty = 0.75 * len(conflicting) / max(len(neg), 1) if neg else 0.0

    score = pos_score + supp_score - neg_penalty
    score = max(0.0, min(score, 1.0))

    return {
        "cell_type": candidate["cell_type"],
        "score": round(score, 4),
        "matched_markers": matched_pos + matched_supp,
        "missing_markers": missing_pos,
        "conflicting_markers": conflicting,
        "explanation": (
            f"matched_pos={len(matched_pos)}, "
            f"matched_supporting={len(matched_supp)}, "
            f"conflicting={len(conflicting)}"
        ),
    }


def rank_candidates(
    query_markers: List[str],
    marker_db: List[Dict[str, Any]],
    species: str = "human",
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    scored = []
    for entry in marker_db:
        if entry.get("species", "human").lower() != species.lower():
            continue
        scored.append(score_candidate(query_markers, entry))

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def assign_confidence_band(
    candidate_scores: List[Dict[str, Any]],
    high_threshold: float = 0.85,
    moderate_threshold: float = 0.65,
    min_gap_high: float = 0.15,
    min_gap_moderate: float = 0.08,
) -> tuple[float, str]:
    if not candidate_scores:
        return 0.0, "low"

    top = candidate_scores[0]["score"]
    second = candidate_scores[1]["score"] if len(candidate_scores) > 1 else 0.0
    gap = top - second

    if top >= high_threshold and gap >= min_gap_high:
        return top, "high"
    if top >= moderate_threshold and gap >= min_gap_moderate:
        return top, "moderate"
    return top, "low"
