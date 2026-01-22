from __future__ import annotations
import math
from typing import Optional, Tuple


def boiling_point_c_at_altitude(altitude_m: float) -> float:
    """
    Approx boiling point vs altitude (rule-of-thumb):
    ~ -0.003 °C per meter (varies with pressure/humidity).
    Good enough for brew planning; mark uncertainty.
    """
    return 100.0 - 0.003 * max(0.0, altitude_m)


def thermal_loss_estimate_c(
    kettle_temp_c: float,
    room_temp_c: float,
    brewer_preheated: bool,
    method: str = "pourover",
) -> Tuple[float, float]:
    """
    Returns (estimated_loss_c, estimated_slurry_peak_c_approx).
    Heuristic model:
      - pourover loses more at contact surfaces and air
      - non-preheated loses more
    This is a proxy—not a measurement. Use slurry probe to validate.
    """
    method = method.lower().strip()
    base_loss = 6.5 if method == "pourover" else 4.0
    preheat_penalty = 0.0 if brewer_preheated else 3.0
    room_penalty = clamp((25.0 - room_temp_c) * 0.08, -1.0, 2.0)
    loss = base_loss + preheat_penalty + room_penalty
    slurry_peak = kettle_temp_c - loss
    return loss, slurry_peak


def extraction_yield_percent(
    tds_percent: float,
    beverage_g: float,
    dose_g: float
) -> float:
    """
    EY% = (TDS% * beverage_mass) / dose_mass
    TDS% is in percent (e.g., 1.35 for 1.35%)
    """
    if dose_g <= 0:
        raise ValueError("dose_g must be > 0")
    if beverage_g <= 0:
        raise ValueError("beverage_g must be > 0")
    return (tds_percent / 100.0) * (beverage_g / dose_g) * 100.0


def contact_time_hint(method: str, total_time_s: Optional[float]) -> str:
    method = method.lower().strip()
    if total_time_s is None:
        return "no_time_measurement"
    if method == "pourover":
        if total_time_s < 150:
            return "short_contact"
        if total_time_s > 270:
            return "long_contact"
        return "normal_contact"
    if method == "immersion":
        if total_time_s < 180:
            return "short_contact"
        if total_time_s > 300:
            return "long_contact"
        return "normal_contact"
    if method == "espresso":
        if total_time_s < 20:
            return "short_contact"
        if total_time_s > 35:
            return "long_contact"
        return "normal_contact"
    return "unknown_method"


def clamp(x: float, a: float, b: float) -> float:
    return max(a, min(b, x))
