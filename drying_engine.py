from __future__ import annotations
from .farmer_models import DryingPlan
from ..proof import ProofLedger


def drying_SOP(plan: DryingPlan, ledger: ProofLedger) -> dict:
    """
    Drying is mass transfer + mold risk control.
    Goal: slow enough to preserve aromatics, fast enough to avoid mold.
    """
    pid = ledger.add(
        kind="axiom",
        claim="Drying is mass transfer; rate must balance aroma preservation and mold risk.",
        basis="energy_transfer",
        inputs={"method": plan.method, "target_moisture_percent": plan.target_moisture_percent},
        output=True
    )

    sop = []
    if plan.method == "raised_bed":
        sop += [
            "ยกแคร่สูง ระบายอากาศทั้งบน-ล่าง",
            "ชั้นหนาไม่เกิน 2–4 ซม. (ช่วงแรกบางหน่อย เพื่อกันร้อนอบใน)",
            "กลับเมล็ดสม่ำเสมอ (อย่างน้อย 6–10 ครั้ง/วันใน 3 วันแรก)",
            "กลางวันแดดจัดให้มี shade dry เพื่อลด ‘ตากแรงจนกลิ่นระเหยหาย’",
        ]
    else:
        sop += [
            "ทำหลักเดียวกัน: คุมความหนา + การกลับ + ป้องกันฝน/น้ำค้าง",
        ]

    sop += [
        f"เป้า moisture ~{plan.target_moisture_percent:.1f}% (ถ้ามี meter วัดจริง)",
        "แยกโซน ‘กลางวัน’ กับ ‘กลางคืน’ (กันน้ำค้างคือเรื่องใหญ่)",
        "ถ้ามีกลิ่นอับ/ราแม้แต่นิดเดียว = สัญญาณว่าระบบ airflow ยังไม่พอ",
    ]

    return {"proofs": [pid], "SOP": sop, "measure_next": ["moisture_percent", "humidity_percent", "bean_temp"]}
