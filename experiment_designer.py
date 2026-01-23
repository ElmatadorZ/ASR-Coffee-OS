from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class Experiment:
    name: str
    hypothesis: str
    variables_controlled: List[str]
    variables_changed: List[str]
    measurement_plan: List[str]
    success_criteria: List[str]
    sample_groups: Dict[str, str]  # group -> description


def design_redfruit_anaerobic_experiment() -> Experiment:
    """
    Win-win template for partnering schools/universities:
    - same cherry lot
    - split into 3 conditions
    - measure simple signals
    """
    return Experiment(
        name="ASR-AN-RED-001",
        hypothesis="Temp control in anaerobic natural shifts ester expression toward red-berry while reducing volatile acidity risk.",
        variables_controlled=["same_lot", "same_vessel_type", "same_fill_ratio", "same_sealing_method", "same_drying_method"],
        variables_changed=["target_temp_c"],
        measurement_plan=[
            "temp log every 6h",
            "smell notes (structured: fruity/floral/solvent/vinegar)",
            "pH every 12h (if possible)",
            "brix start & end (if possible)",
            "cupping notes after resting (internal panel)"
        ],
        success_criteria=[
            "red berry aroma ↑",
            "no vinegar/solvent notes",
            "clean finish",
            "stable drying (no mold/off)"
        ],
        sample_groups={
            "G1": "18–19C (cool control)",
            "G2": "21–23C (target window)",
            "G3": "26–27C (warm edge)"
        }
    )
