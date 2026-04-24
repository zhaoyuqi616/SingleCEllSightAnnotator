from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    curated_marker_db: str = os.getenv(
        "CURATED_MARKER_DB", "data/knowledge/curated_markers_v1.json"
    )
    output_dir: str = os.getenv("OUTPUT_DIR", "outputs")
    species_default: str = "human"
    top_k_candidates: int = 5
    high_confidence_threshold: float = 0.85
    moderate_confidence_threshold: float = 0.65
    min_score_gap_high: float = 0.15
    min_score_gap_moderate: float = 0.08

settings = Settings()
