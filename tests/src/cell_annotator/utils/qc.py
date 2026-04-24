from __future__ import annotations
from typing import List

STRESS_GENES = {"FOS", "JUN", "HSPA1A", "HSPB1", "DNAJB1"}
CELL_CYCLE_GENES = {"MKI67", "TOP2A", "UBE2C", "PCNA", "STMN1"}
RBC_GENES = {"HBA1", "HBA2", "HBB", "ALAS2"}


def qc_flags_for_markers(markers: List[str]) -> List[str]:
    flags = []
    mset = set(markers)

    if len(markers) < 3:
        flags.append("too_few_markers")

    if len(mset & STRESS_GENES) >= 2:
        flags.append("stress_signature")

    if len(mset & CELL_CYCLE_GENES) >= 2:
        flags.append("cell_cycle_signature")

    if len(mset & RBC_GENES) >= 2:
        flags.append("possible_rbc_contamination")

    if ("EPCAM" in mset and "PTPRC" in mset) or ("MS4A1" in mset and "LYZ" in mset):
        flags.append("possible_doublet")

    return flags
