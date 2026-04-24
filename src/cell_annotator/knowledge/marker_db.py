from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any


def load_marker_db(path: str) -> List[Dict[str, Any]]:
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Curated marker DB not found: {path}")
    with open(path_obj, "r") as f:
        return json.load(f)
