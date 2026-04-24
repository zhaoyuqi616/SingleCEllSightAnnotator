from __future__ import annotations
import json
from typing import List, Dict, Any


def format_candidate_scores(candidate_scores: List[Dict[str, Any]]) -> str:
    return json.dumps(candidate_scores, indent=2)
