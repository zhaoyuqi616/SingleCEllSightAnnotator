from __future__ import annotations
from typing import Dict, Iterable, List, Tuple

GENE_ALIAS_MAP: Dict[str, str] = {
    "PD-L1": "CD274",
    "PD1": "PDCD1",
    "CTLA-4": "CTLA4",
    "FOXP-3": "FOXP3",
    "CD-3D": "CD3D",
}


def normalize_gene_symbol(gene: str) -> str:
    gene_raw = str(gene).strip()
    gene_upper = gene_raw.upper()
    return GENE_ALIAS_MAP.get(gene_raw, GENE_ALIAS_MAP.get(gene_upper, gene_upper))


def normalize_gene_list(genes: Iterable[str]) -> Tuple[List[str], List[str]]:
    normalized = []
    unmapped = []

    for g in genes:
        ng = normalize_gene_symbol(g)
        if not ng or ng == "NAN":
            unmapped.append(str(g))
            continue
        normalized.append(ng)

    seen = set()
    dedup = []
    for g in normalized:
        if g not in seen:
            dedup.append(g)
            seen.add(g)

    return dedup, unmapped
