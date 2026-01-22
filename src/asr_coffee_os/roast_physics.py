from __future__ import annotations
from typing import Optional, Dict
import math


def thermal_momentum(
    bean_temp_c: float,
    environment_temp_c: float,
    ror_c_per_min: float,
) -> float:
    """
    Thermal Momentum (proxy):
    ความสามารถของระบบในการพาอุณหภูมิไปต่อ
    ไม่ใช่แค่ความร้อน แต่คือ 'ทิศทาง'
    """
    delta = environment_temp_c - bean_temp_c
    return max(0.0, delta) * max(0.1, ror_c_per_min)


def development_ratio(dev_time_s: float, total_time_s: float) -> float:
    if total_time_s <= 0:
        raise ValueError("total_time_s must be > 0")
    return dev_time_s / total_time_s


def roast_stability_index(
    ror_variance: float,
    airflow_changes: int,
) -> float:
    """
    RSI (0–1):
    1 = stable roast, 0 = chaotic
    """
    penalty = ror_variance * 0.6 + airflow_changes * 0.4
    return max(0.0, 1.0 - penalty)
