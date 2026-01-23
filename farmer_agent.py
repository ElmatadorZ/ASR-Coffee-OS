from __future__ import annotations
from typing import List
from .farmer_models import FarmContext, CherryLot, FermentationPlan, FermentationLog, DryingPlan, FarmerReport
from .field_assessment import assess_raw_material
from .fermentation_engine import recommend_anaerobic_natural
from .drying_engine import drying_SOP
from ..proof import ProofLedger
from ..codex import FirstPrincipleCodex


class FarmerModeAgent:
    def __init__(self) -> None:
        self.codex = FirstPrincipleCodex()

    def run(
        self,
        farm: FarmContext,
        lot: CherryLot,
        ferm_plan: FermentationPlan,
        ferm_logs: List[FermentationLog],
        dry_plan: DryingPlan
    ) -> FarmerReport:
        ledger = ProofLedger()

        triage = assess_raw_material(farm, lot, ledger)
        if triage["status"] != "ok":
            return FarmerReport(
                summary="ยังไม่พอจะวางโปรเซสแบบปลอดการเดา: ต้องวัดวัตถุดิบก่อน",
                action_now=[
                    "วัด Brix, %สุก, %ลอยน้ำ (floaters) ของล็อตนี้",
                    "ถ่ายรูปการคัดเชอร์รี่/ความสุกเพื่อทำ baseline"
                ],
                risks=["ถ้าข้ามขั้นนี้ การหมักจะขยาย defect แทนที่จะสร้างกลิ่นผลไม้"],
                what_to_measure_next=triage["missing"],
                SOP=["ทำ checklist วัตถุดิบก่อนทุกโปรเซส (เพื่อให้โปรเซสเป็นสินทรัพย์ระยะยาว)"],
                confidence=0.9,
                proof_ledger=ledger.export()
            )

        ceiling = triage["ceiling"]

        ferm = recommend_anaerobic_natural(lot, ferm_plan, ferm_logs, ledger)
        if ferm["status"] != "ok":
            return FarmerReport(
                summary=f"วัตถุดิบเพดาน {ceiling} แต่ยังขาดตัวแปรหลักของการหมัก",
                action_now=[
                    "กำหนด target_temp_c และ target_hours ก่อนลงถัง",
                    "เตรียมวิธีคุมอุณหภูมิ: ห้องเย็น/น้ำแข็ง/ผ้าคลุม/ย้ายตำแหน่งถัง"
                ],
                risks=["หมักแบบไม่มี constraint = เสี่ยงกลิ่นฉุน/น้ำส้ม/solvent"],
                what_to_measure_next=ferm["missing"],
                SOP=["ตั้งระบบ log ทุก 6 ชม. (temp + กลิ่น + ภาพ)"],
                confidence=0.86,
                proof_ledger=ledger.export()
            )

        dry = drying_SOP(dry_plan, ledger)

        # Compose final report
        summary = (
            f"Farmer Mode (ASR): เพดานวัตถุดิบ = {ceiling}\n"
            "โหมดนี้จะไม่เดา: ทุกคำแนะนำยืนบนการวัด+ข้อจำกัด\n"
            "เป้าคือทำให้โปรเซสของคุณ ‘ทำซ้ำได้’ และส่งต่อเป็นหลักสูตรได้"
        )

        action_now = []
        action_now += ferm["action"]
        action_now += ["เริ่ม Drying ตาม SOP และคุม ‘น้ำค้าง + airflow’ เป็นอันดับหนึ่ง"]
        action_now += ["เก็บตัวอย่าง 200–300g ต่อกลุ่ม เพื่อ cupping หลังพัก (ทำเป็นฐานข้อมูลของฟาร์ม)"]

        risks = ferm["risks"] + ["การตากแรงเกินไปทำให้กลิ่นผลไม้ ‘ระเหยหาย’ ก่อนล็อกคุณภาพ"]

        measure_next = sorted(set(ferm["monitor"] + dry["measure_next"]))

        sop = []
        sop += ["== Fermentation Stop Rules =="] + ferm["stop_rules"]
        sop += ["== Drying SOP =="] + dry["SOP"]

        return FarmerReport(
            summary=summary,
            action_now=action_now,
            risks=risks,
            what_to_measure_next=measure_next,
            SOP=sop,
            confidence=0.82 if ceiling != "high" else 0.9,
            proof_ledger=ledger.export()
        )
