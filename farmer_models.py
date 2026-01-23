from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass(frozen=True)
class FarmContext:
    farm_name: str = "unknown"
    location: str = ""
    altitude_m: Optional[float] = None
    avg_temp_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    rainfall_mm_week: Optional[float] = None
    shade_percent: Optional[float] = None
    soil_notes: str = ""
    variety: str = "unknown"
    harvest_month: str = ""
    notes: str = ""


@dataclass(frozen=True)
class CherryLot:
    lot_id: str
    harvest_date: str  # YYYY-MM-DD
    ripeness_percent: Optional[float] = None  # % fully ripe
    brix: Optional[float] = None
    floaters_percent: Optional[float] = None
    defects_notes: str = ""
    weight_kg: Optional[float] = None


@dataclass(frozen=True)
class FermentationPlan:
    process: str  # "anaerobic_natural" | "anaerobic_washed" | "honey" ...
    target_profile: str = "red_berry"
    vessel: str = "tank"  # tank, barrel, bag, etc.
    inoculation: str = "wild"  # wild / yeast / lacto / mixed
    target_temp_c: Optional[float] = None
    target_hours: Optional[float] = None
    oxygen_control: str = "sealed"  # sealed / airlock / semi
    agitation: str = "none"  # none / gentle / periodic
    notes: str = ""


@dataclass(frozen=True)
class FermentationLog:
    time_h: float
    temp_c: Optional[float] = None
    ph: Optional[float] = None
    brix: Optional[float] = None
    smell_notes: str = ""
    visual_notes: str = ""


@dataclass(frozen=True)
class DryingPlan:
    method: str  # raised_bed / patio / solar_dome
    target_moisture_percent: float = 11.0
    target_aw: Optional[float] = None  # water activity
    layer_cm: Optional[float] = None
    turn_per_day: Optional[int] = None
    shade_dry: bool = True
    notes: str = ""


@dataclass
class FarmerReport:
    summary: str
    action_now: List[str]
    risks: List[str]
    what_to_measure_next: List[str]
    SOP: List[str]
    confidence: float
    proof_ledger: Dict[str, Any]
