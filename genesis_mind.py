from typing import List
from .codex import FirstPrincipleCodex
from .proof import ProofLedger

class GenesisMind:
    def __init__(self):
        self.codex = FirstPrincipleCodex()
        self.ledger = ProofLedger()

    def think(self, question: str, inputs: dict) -> dict:
        if not inputs:
            return {
                "status": "refused",
                "reason": "No data → no reality → no answer"
            }

        pid = self.ledger.add(
            kind="axiom",
            claim="No answer without physical grounding",
            basis="reality_constraint",
            inputs=inputs,
            output=True
        )

        return {
            "status": "thinking",
            "approach": "first principle reduction",
            "proof": pid
        }
