from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional


class AlternativeLabel(BaseModel):
    label: str
    reason: str


class AdjudicationOutput(BaseModel):
    selected_label: str = Field(..., description="Best supported cell type label")
    confidence_band: str = Field(..., description="high, moderate, low")
    matched_markers: List[str] = Field(default_factory=list)
    rationale: str = Field(..., description="Brief scientific explanation")
    review_required: bool = Field(default=False)
    review_notes: Optional[str] = None
    alternatives: List[AlternativeLabel] = Field(default_factory=list)
