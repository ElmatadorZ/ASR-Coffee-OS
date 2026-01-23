from __future__ import annotations
from .farmer_models import FarmContext, CherryLot
from ..proof import ProofLedger


def assess_raw_material(farm: FarmContext, lot: CherryLot, ledger: ProofLedger) -> dict:
    """
    Physics-first mindset:
    Raw material quality sets the ceiling.
    If ceiling low, fermentation becomes risk amplifier.
    """
    missing = []
    if lot.brix is None: missing.append("brix")
    if lot.ripeness_percent is None: missing.append("ripeness_percent")
    if lot.floaters_percent is None: missing.append("floaters_percent")

    pid = ledger.add(
        kind="axiom",
        claim="Raw material quality sets the ceiling; process cannot exceed raw constraints.",
        basis="constraints",
        inputs={"brix": lot.brix, "ripeness_percent": lot.ripeness_percent, "floaters_percent": lot.floaters_percent},
        output=True
    )

    # conservative triage (no guessing)
    if missing:
        return {
            "status": "need_measurements",
            "missing": missing,
            "ceiling": "unknown",
            "proof": pid
        }

    ceiling = "high"
    if lot.brix < 18 or lot.ripeness_percent < 75 or lot.floaters_percent > 8:
        ceiling = "medium"
    if lot.brix < 16 or lot.ripeness_percent < 60 or lot.floaters_percent > 15:
        ceiling = "low"

    pid2 = ledger.add(
        kind="equation",
        claim="Ceiling classification from Brix/ripeness/floaters (conservative triage).",
        basis="triage_rules_v1",
        inputs={"brix": lot.brix, "ripeness_percent": lot.ripeness_percent, "floaters_percent": lot.floaters_percent},
        output=ceiling,
        uncertainty="field proxy (not lab cupping)"
    )

    return {"status": "ok", "ceiling": ceiling, "proofs": [pid, pid2]}
