from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any, Dict, List


@dataclass(frozen=True)
class Axiom:
    key: str
    statement: str
    test: Callable[[Any], bool]
    notes: str = ""


class FirstPrincipleCodex:
    """
    ASR Codex: the rules you cannot cheat.
    """
    def __init__(self) -> None:
        self.axioms: Dict[str, Axiom] = {}
        self._bootstrap()

    def _bootstrap(self) -> None:
        self.add("constraints", "Reality is bounded by constraints (energy/time/material).", lambda _: True,
                 "Kill magical thinking.")
        self.add("energy_transfer", "Extraction is an energy + mass transfer problem.", lambda _: True,
                 "Temperature & contact govern rate.")
        self.add("measurement", "If you cannot measure/proxy it, treat it as uncertain.", lambda _: True,
                 "Uncertainty must be stated, not hidden.")
        self.add("causation", "Effects trace to root causes; avoid single-cause stories.", lambda _: True,
                 "Use system interactions.")
        self.add("entropy", "Without directed control, quality drifts.", lambda _: True,
                 "Stability requires process control.")
        self.add("no_guessing", "If inputs are missing, request them; do not fabricate.", lambda _: True,
                 "Hallucination goes to ~0 by refusing.")

    def add(self, key: str, statement: str, test: Callable[[Any], bool], notes: str = "") -> None:
        self.axioms[key] = Axiom(key, statement, test, notes)

    def rules(self) -> List[str]:
        return [f"{a.key}: {a.statement}" for a in self.axioms.values()]
