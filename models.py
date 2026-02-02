# ================================
# FILE: src/asr_coffee_os/models.py
# ================================
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass(frozen=True)
class BrewInputs:
    method: str = "pourover"  # pourover, espresso, immersion
    dose_g: Optional[float] = None
    water_g: Optional[float] = None
    beverage_g: Optional[float] = None
    grind_setting: Optional[str] = None
    kettle_temp_c: Optional[float] = None
    room_temp_c: Optional[float] = None
    brewer_preheated: Optional[bool] = None
    bloom: Optional[bool] = None
    total_time_s: Optional[float] = None
    altitude_m: Optional[float] = None
    tds_percent: Optional[float] = None
    slurry_temp_c: Optional[float] = None
    notes: str = ""

@dataclass(frozen=True)
class RoastInputs:
    bean: str = "unknown"
    batch_g: Optional[float] = None
    density_g_ml: Optional[float] = None
    charge_temp_c: Optional[float] = None
    end_temp_c: Optional[float] = None
    dev_time_s: Optional[float] = None
    total_time_s: Optional[float] = None
    ror_c_per_min: Optional[float] = None
    environment: str = ""
    notes: str = ""

# ✅ NEW: Green Bean Inputs (aW / Moisture / Storage system)
@dataclass(frozen=True)
class GreenBeanInputs:
    bean: str = "unknown"
    origin: str = ""
    process: str = ""  # washed/natural/honey/anaerobic/etc.

    # core measures
    moisture_percent: Optional[float] = None   # Moisture Content (%)
    aw: Optional[float] = None                # Water Activity (aW)

    # optional quality proxies (not mandatory)
    density_g_ml: Optional[float] = None
    screen: Optional[int] = None

    # storage system (System Thinking)
    storage_temp_c: Optional[float] = None
    storage_rh_percent: Optional[float] = None
    bag_on_floor: Optional[bool] = None
    ventilation_ok: Optional[bool] = None
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
    proof_ledger: Dict[str, Any] = field(default_factory=dict)
