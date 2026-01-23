from dataclasses import dataclass
from typing import Optional

@dataclass
class RoastState:
    bean_temp_c: float
    env_temp_c: float
    ror_c_per_min: float
    time_s: float
    dev_time_s: float
    first_crack_s: Optional[float]

def thermal_momentum(ror: float, mass_g: float) -> float:
    """
    Thermal Momentum = Rate of Energy Accumulation
    High momentum late roast = overshoot risk
    """
    return ror * (mass_g / 1000)

def dev_ratio(dev_time: float, total_time: float) -> float:
    if total_time == 0:
        raise ValueError("total_time must > 0")
    return dev_time / total_time

def roast_risk_analysis(state: RoastState, mass_g: float) -> dict:
    momentum = thermal_momentum(state.ror_c_per_min, mass_g)
    ratio = dev_ratio(state.dev_time_s, state.time_s)

    risk = "stable"
    if momentum > 1.2 and ratio > 0.22:
        risk = "baked / flat risk"
    elif momentum < 0.6 and ratio < 0.16:
        risk = "underdeveloped risk"

    return {
        "thermal_momentum": momentum,
        "development_ratio": ratio,
        "risk_assessment": risk
    }
