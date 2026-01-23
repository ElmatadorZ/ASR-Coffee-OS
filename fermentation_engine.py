from __future__ import annotations
from typing import List
from .farmer_models import CherryLot, FermentationPlan, FermentationLog
from ..proof import ProofLedger


def recommend_anaerobic_natural(
    lot: CherryLot,
    plan: FermentationPlan,
    logs: List[FermentationLog],
    ledger: ProofLedger
) -> dict:
    """
    Output is bounded: if no key measurements, return what to measure.
    Goal: red berry = ester-friendly window but avoid acetic/vinegar.
    """
    missing = []
    if lot.brix is None: missing.append("brix")
    if plan.target_temp_c is None: missing.append("target_temp_c")
    if plan.target_hours is None: missing.append("target_hours")

    pid0 = ledger.add(
        kind="axiom",
        claim="Fermentation is controlled biology under constraints; missing constraints => no safe prediction.",
        basis="measurement",
        inputs={"brix": lot.brix, "target_temp_c": plan.target_temp_c, "target_hours": plan.target_hours},
        output=True
    )

    if missing:
        return {"status": "need_measurements", "missing": missing, "proof": pid0}

    # Simple safe window (field default)
    # Red berry target: 20–24C often helps fruity esters; >28C increases volatile acidity risk.
    risks = []
    if plan.target_temp_c > 28:
        risks.append("อุณหภูมิสูง เสี่ยง acetic/น้ำส้ม/กลิ่นฉุน")
    if plan.target_temp_c < 18:
        risks.append("อุณหภูมิต่ำ อาจได้กลิ่นผลไม้ไม่ขึ้น/โปรไฟล์นิ่ง")

    pid1 = ledger.add(
        kind="equation",
        claim="Safe temp window heuristic for ester vs acetic risk.",
        basis="temp_window_v1",
        inputs={"target_temp_c": plan.target_temp_c},
        output={"target_window": "20-24C", "risk_high_temp": ">28C", "risk_low_temp": "<18C"},
        uncertainty="depends on microbes, vessel, oxygen control"
    )

    # Decision using logs (if present)
    action = []
    monitor = ["temp_c", "smell_notes"]
    if any(l.ph is not None for l in logs):
        monitor.append("ph")
    if any(l.brix is not None for l in logs):
        monitor.append("brix")

    # Conservative stopping rules
    stop_rules = [
        "ถ้ากลิ่นเริ่มฉุนคล้ายน้ำส้ม/ทินเนอร์ → หยุด/เข้า drying ทันที",
        "ถ้าอุณหภูมิในถังพุ่งและคุมไม่ได้ → เปิดระบาย/ลดโหลด/ย้ายไปที่เย็น",
        "ถ้า pH (ถ้าวัดได้) ลดเร็วผิดปกติ → เสี่ยง over-ferment ให้หยุดเร็วขึ้น",
    ]

    action += [
        f"ตั้งเป้าอุณหภูมิถัง {plan.target_temp_c:.1f}°C (พยายามคุมให้อยู่ในช่วง 20–24°C ถ้าอยากได้ red berry ชัด)",
        f"ตั้งเวลา {plan.target_hours:.0f} ชม. แต่ให้ ‘หยุดตามสัญญาณ’ ไม่ใช่หยุดตามนาฬิกาอย่างเดียว",
        "ใช้ระบบปิด (sealed/airlock) ลด oxygen เพื่อคุม acetic",
        "จด log ทุก 6 ชม. (อุณหภูมิ + กลิ่น + ภาพ) เพื่อให้โปรเซสกลายเป็นทรัพย์สินของคุณ",
    ]

    return {
        "status": "ok",
        "action": action,
        "monitor": monitor,
        "stop_rules": stop_rules,
        "risks": risks,
        "proofs": [pid0, pid1],
    }
