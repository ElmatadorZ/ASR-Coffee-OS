from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Proof:
    """
    Proof is the anti-hallucination backbone.
    Anything asserted must reference a Proof ID.
    """
    id: str
    kind: str  # "equation" | "measurement" | "axiom" | "assumption"
    claim: str
    basis: str  # e.g., equation name, measurement key, axiom key
    inputs: Dict[str, Any]
    output: Any
    notes: str = ""
    uncertainty: Optional[str] = None


class ProofLedger:
    def __init__(self) -> None:
        self._items: Dict[str, Proof] = {}
        self._n = 0

    def add(self, kind: str, claim: str, basis: str, inputs: Dict[str, Any], output: Any,
            notes: str = "", uncertainty: str | None = None) -> str:
        self._n += 1
        pid = f"P{self._n:04d}"
        self._items[pid] = Proof(
            id=pid, kind=kind, claim=claim, basis=basis,
            inputs=inputs, output=output, notes=notes, uncertainty=uncertainty
        )
        return pid

    def export(self) -> Dict[str, Any]:
        return {k: vars(v) for k, v in self._items.items()}

    def get(self, pid: str) -> Proof:
        return self._items[pid]
