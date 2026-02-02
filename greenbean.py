# ==================================
# FILE: src/asr_coffee_os/greenbean.py
# ==================================
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any

# -----------------------------
# Threshold Config (Configurable)
# -----------------------------
@dataclass(frozen=True)
class AWThresholds:
    sweet_low: float = 0.50
    sweet_high: float = 0.57
    caution_low: float = 0.58
    caution_high: float = 0.62
    danger_over: float = 0.62
    too_low_under: float = 0.45

@dataclass(frozen=True)
class MoistureThresholds:
    # Typical reference window used by many roasters; not absolute truth.
    low: float = 9.0
    good_low: float = 9.5
    good_high: float = 11.5
    high: float = 12.5

DEFAULT_AW = AWThresholds()
DEFAULT_MC = MoistureThresholds()

def classify_aw(aw: float, th: AWThresholds = DEFAULT_AW) -> Dict[str, Any]:
    """
    Classify water activity into stability/risk buckets.
    Returns dict with: tag, meaning, risk_vector (storage/mold/aging).
    """
    if aw < th.too_low_under:
        return {
            "tag": "too_low",
            "meaning": "อาจแห้งเกิน/พลังในเมล็ดลด/โครงสร้างอาจเสื่อม",
            "risk_vector": ["ถ้วยบาง", "sweetness ลด", "body เบา"],
        }
    if th.sweet_low <= aw <= th.sweet_high:
        return {
            "tag": "sweet_spot",
            "meaning": "เสถียรภาพสูง (น้ำมี activity ต่ำพอที่จะชะลอการเสื่อมและเชื้อรา)",
            "risk_vector": ["เสถียร", "เก็บได้นานกว่า", "คั่วคาดการณ์ง่ายกว่า"],
        }
    if th.caution_low <= aw <= th.caution_high:
        return {
            "tag": "caution",
            "meaning": "เสี่ยงเสื่อมเร็วขึ้นแบบหลอกตา (ยังดูดีแต่ aging เร็ว)",
            "risk_vector": ["aroma drop", "acidity drop", "shelf life สั้น"],
        }
    if aw > th.danger_over:
        return {
            "tag": "danger",
            "meaning": "โซนเสี่ยงสูง (mold / defect / safety risk) ต้องจัดการ storage ทันที",
            "risk_vector": ["เชื้อรา", "baggy", "ความเสี่ยงด้านความปลอดภัยอาหาร"],
        }
    # between sweet_high and caution_low
    return {
        "tag": "transition",
        "meaning": "ก้ำกึ่ง: ไม่แย่ แต่เริ่มไวต่อสภาพแวดล้อมมากขึ้น",
        "risk_vector": ["ต้องคุมโกดัง", "อย่าเก็บนานเกิน"],
    }

def classify_moisture(moisture_percent: float, th: MoistureThresholds = DEFAULT_MC) -> Dict[str, Any]:
    if moisture_percent < th.low:
        return {"tag": "too_dry", "meaning": "แห้งมาก: เสี่ยงถ้วยบาง/พลังลด", "risk_vector": ["thin cup"]}
    if th.good_low <= moisture_percent <= th.good_high:
        return {"tag": "ok", "meaning": "อยู่ในช่วงใช้งานทั่วไปของโรงคั่วจำนวนมาก", "risk_vector": ["stable"]}
    if moisture_percent > th.high:
        return {"tag": "too_wet", "meaning": "ชื้นสูง: เสี่ยงเชื้อรา/เสื่อมเร็ว", "risk_vector": ["mold risk"]}
    return {"tag": "border", "meaning": "ก้ำกึ่ง: ควรดู aW และ storage ร่วม", "risk_vector": ["monitor"]}

def storage_risk_notes(storage_rh_percent: Optional[float], bag_on_floor: Optional[bool],
                       ventilation_ok: Optional[bool]) -> Dict[str, Any]:
    notes = []
    risk = "unknown"

    if storage_rh_percent is None and bag_on_floor is None and ventilation_ok is None:
        return {"risk": "unknown", "notes": ["ไม่มีข้อมูลโกดัง/ความชื้นอากาศ: ประเมินระบบเก็บรักษาไม่ได้"]}

    # rough heuristics (not claiming universal truth)
    if storage_rh_percent is not None:
        if storage_rh_percent >= 70:
            notes.append("RH สูง: เมล็ดดูดความชื้นจากอากาศได้เร็ว โดยเฉพาะฤดูฝน/พื้นที่ปิด")
            risk = "high"
        elif storage_rh_percent >= 60:
            notes.append("RH กลาง-สูง: ต้องคุม airflow/พื้น/ผนัง/การวางกระสอบ")
            risk = "medium"
        else:
            notes.append("RH ค่อนข้างต่ำ: ความเสี่ยงดูดความชื้นลดลง แต่ยังต้องกันคอนเทนเนอร์เหงื่อ")
            risk = "low"

    if bag_on_floor is True:
        notes.append("วางกระสอบติดพื้น: เพิ่มโอกาสดูดชื้น + transfer จากพื้น/ผนัง")
        risk = "high" if risk != "unknown" else "medium"

    if ventilation_ok is False:
        notes.append("ระบายอากาศไม่ดี: เพิ่มโอกาส container sweating/กลิ่นกระสอบ/ความชื้นสะสม")
        risk = "high" if risk != "unknown" else "medium"

    return {"risk": risk, "notes": notes}
