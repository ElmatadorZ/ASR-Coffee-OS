from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass(frozen=True)
class BrewInputs:
    method: str = "pourover"  # pourover, espresso, immersion
    dose_g: Optional[float] = None
    water_g: Optional[float] = None
    beverage_g: Optional[float] = None  # esp. for espresso/immersion
    grind_setting: Optional[str] = None  # descriptive, not numeric
    kettle_temp_c: Optional[float] = None
    room_temp_c: Optional[float] = None
    brewer_preheated: Optional[bool] = None
    bloom: Optional[bool] = None
    total_time_s: Optional[float] = None
    altitude_m: Optional[float] = None

    # measurements (optional but recommended)
    tds_percent: Optional[float] = None  # beverage TDS
    slurry_temp_c: Optional[float] = None  # measured slurry
    notes: str = ""


@dataclass(frozen=True)
class RoastInputs:
    bean: str = "unknown"
    batch_g: Optional[float] = None
    density_g_ml: Optional[float] = None  # proxy
    charge_temp_c: Optional[float] = None
    end_temp_c: Optional[float] = None
    dev_time_s: Optional[float] = None
    total_time_s: Optional[float] = None
    ror_c_per_min: Optional[float] = None
    environment: str = ""
    notes: str = ""


@dataclass
class Recommendation:
    title: str
    steps: List[str]
    why: List[str] = field(default_factory=list)
    what_to_measure: List[str] = field(default_factory=list)
    confidence: float = 0.0
    proof_refs: List[str] = field(default_factory=list)


@dataclass
class AnalysisReport:
    summary: str
    recommendations: List[Recommendation]
    missing_inputs: List[str] = field(default_factory=list)
    proof_ledger: Dict[str, Any] = field(default_factory=dict)  # id -> proof object
