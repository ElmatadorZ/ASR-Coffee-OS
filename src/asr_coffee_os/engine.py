from __future__ import annotations
from typing import List, Dict, Any
from .models import BrewInputs, AnalysisReport, Recommendation
from .codex import FirstPrincipleCodex
from .proof import ProofLedger
from . import physics


class CoffeeOS:
    """
    Physics-first Coffee AI OS:
    - Only produces claims that have proofs
    - If missing critical inputs, it returns missing list + what to measure next
    """

    def __init__(self) -> None:
        self.codex = FirstPrincipleCodex()

    def analyze_brew(self, inp: BrewInputs) -> AnalysisReport:
        ledger = ProofLedger()
        missing: List[str] = self._missing_for_brew(inp)

        # Codex rule: no guessing
        p_axiom = ledger.add(
            kind="axiom",
            claim="If inputs are missing, request them; do not fabricate.",
            basis="no_guessing",
            inputs={},
            output=True,
            notes="ASR Codex anti-hallucination rule"
        )

        if missing:
            rec = Recommendation(
                title="ต้องการข้อมูลเพิ่มเพื่อวิเคราะห์แบบไม่เดา (มั่ว≈0%)",
                steps=[
                    "วัด/กรอกตัวแปรที่ขาดตามรายการ Missing inputs",
                    "ถ้ามี Refractometer ให้ใส่ TDS% และ beverage weight เพื่อคำนวณ EY%",
                    "ถ้ามี probe ให้วัด slurry temperature เพื่อยืนยัน thermal loss",
                ],
                why=[
                    "การชงเป็นปัญหา energy + mass transfer; ถ้าตัวแปรหลักหาย การเดาจะพาคุณออกนอกฟิสิกส์",
                    "ระบบที่ไม่เดา จะพาคุณสู่สกิลที่นำไปใช้ซ้ำได้ทุกเมล็ด ทุก environment",
                ],
                what_to_measure=missing,
                confidence=0.92,
                proof_refs=[p_axiom],
            )
            return AnalysisReport(
                summary="ข้อมูลยังไม่พอสำหรับข้อสรุปเชิงฟิสิกส์แบบรับผิดชอบ (ระบบจะไม่เดา).",
                recommendations=[rec],
                missing_inputs=missing,
                proof_ledger=ledger.export(),
            )

        # ---- 1) Boiling point (altitude) ----
        bp = 100.0
        bp_uncertainty = None
        if inp.altitude_m is not None:
            bp = physics.boiling_point_c_at_altitude(inp.altitude_m)
            bp_uncertainty = "rule-of-thumb; pressure/humidity not included"
        p_bp = ledger.add(
            kind="equation",
            claim="boiling point changes with altitude, shifting your max brew temp ceiling",
            basis="boiling_point_c_at_altitude",
            inputs={"altitude_m": inp.altitude_m},
            output=bp,
            uncertainty=bp_uncertainty
        )

        # ---- 2) Thermal loss (proxy if slurry not measured) ----
        loss_c, slurry_peak = physics.thermal_loss_estimate_c(
            kettle_temp_c=inp.kettle_temp_c or 96.0,
            room_temp_c=inp.room_temp_c or 25.0,
            brewer_preheated=bool(inp.brewer_preheated),
            method=inp.method,
        )
        p_loss = ledger.add(
            kind="equation",
            claim="slurry temp is typically lower than kettle temp due to thermal loss",
            basis="thermal_loss_estimate_c",
            inputs={
                "kettle_temp_c": inp.kettle_temp_c,
                "room_temp_c": inp.room_temp_c,
                "brewer_preheated": inp.brewer_preheated,
                "method": inp.method
            },
            output={"loss_c": loss_c, "slurry_peak_est_c": slurry_peak},
            notes="This is a proxy. Use slurry probe to convert proxy->measurement.",
            uncertainty="heuristic model"
        )

        slurry_truth = inp.slurry_temp_c if inp.slurry_temp_c is not None else slurry_peak
        p_slurry = ledger.add(
            kind="measurement" if inp.slurry_temp_c is not None else "assumption",
            claim="slurry temperature used for reasoning",
            basis="slurry_temp_c",
            inputs={"slurry_temp_c": inp.slurry_temp_c, "slurry_peak_est_c": slurry_peak},
            output=slurry_truth,
            notes="Measured beats estimated.",
            uncertainty=None if inp.slurry_temp_c is not None else "estimated"
        )

        # ---- 3) Contact time hint ----
        time_tag = physics.contact_time_hint(inp.method, inp.total_time_s)
        p_time = ledger.add(
            kind="equation",
            claim="contact time category influences extraction tendency",
            basis="contact_time_hint",
            inputs={"method": inp.method, "total_time_s": inp.total_time_s},
            output=time_tag
        )

        # ---- 4) EY% if measured ----
        ey = None
        p_ey = None
        if inp.tds_percent is not None and inp.beverage_g is not None and inp.dose_g is not None:
            ey = physics.extraction_yield_percent(inp.tds_percent, inp.beverage_g, inp.dose_g)
            p_ey = ledger.add(
                kind="equation",
                claim="Extraction Yield can be computed from TDS, beverage mass, and dose",
                basis="extraction_yield_percent",
                inputs={"tds_percent": inp.tds_percent, "beverage_g": inp.beverage_g, "dose_g": inp.dose_g},
                output=ey
            )

        # ---- Build recommendations (proof-gated) ----
        recs: List[Recommendation] = []

        # Temperature strategy (physics)
        temp_steps = []
        temp_why = []
        proof_refs = [p_bp, p_loss, p_slurry]

        # cap by boiling point
        max_possible = min(inp.kettle_temp_c or 96.0, bp)
        p_cap = ledger.add(
            kind="equation",
            claim="kettle temperature cannot exceed local boiling point ceiling",
            basis="min(kettle, boiling_point)",
            inputs={"kettle_temp_c": inp.kettle_temp_c, "boiling_point_c": bp},
            output=max_possible,
            uncertainty=bp_uncertainty
        )
        proof_refs.append(p_cap)

        temp_steps.append(f"ตั้งอุณหภูมิกาต้มน้ำให้ใกล้เพดานที่เป็นไปได้: ~{max_possible:.1f}°C (ขึ้นกับความสูง/เดือดจริง)")
        temp_steps.append("ถ้าอยาก ‘ไม่เดา’ ให้ใช้ probe วัด slurry temp แล้วปรับ kettle เพื่อให้ slurry เข้าเป้าหมาย")
        temp_why.append("ในฟิสิกส์: สิ่งที่ทำงานกับผงกาแฟจริง ๆ คือ slurry temp ไม่ใช่ตัวเลขหน้ากา")
        temp_why.append("การปรับด้วย slurry = ชดเชย thermal loss ตามระบบจริงของคุณ")

        recs.append(Recommendation(
            title="อุณหภูมิแบบ ASR: ปรับด้วย ‘อุณหภูมิในแก้ว (slurry)’ ไม่ใช่ตัวเลขหน้ากา",
            steps=temp_steps,
            why=temp_why,
            what_to_measure=[
                "slurry_temp_c (ถ้ามี probe)",
                "kettle_temp_c (วัดจริง)",
                "room_temp_c / preheat state",
            ],
            confidence=0.78 if inp.slurry_temp_c is None else 0.9,
            proof_refs=proof_refs,
        ))

        # Time / grind / ratio suggestions (still bounded)
        time_steps = []
        time_why = []
        proof_refs2 = [p_time]

        if time_tag == "short_contact":
            time_steps += [
                "ถ้ารส ‘บาง/เปรี้ยวโดด/หวานไม่มา’: เพิ่ม contact time ทีละน้อย (ช้าลงเล็กน้อย หรือบดละเอียดขึ้นเล็กน้อย)",
                "คุมอย่างเดียวทีละตัวแปร เพื่อเห็นเหตุ-ผลจริง",
            ]
            time_why += [
                "contact time สั้น → โอกาส under-extraction สูงขึ้น โดยเฉพาะเมล็ด density สูง",
            ]
        elif time_tag == "long_contact":
            time_steps += [
                "ถ้ารส ‘ฝาด/ขม/แห้ง’: ลด contact time ทีละน้อย (ไหลเร็วขึ้น หรือบดหยาบขึ้นเล็กน้อย)",
                "ตรวจว่ามี channeling/การเทที่ทำให้บางจุดสกัดเกินไหม",
            ]
            time_why += [
                "contact time ยาว → ความเสี่ยง over-extraction เพิ่ม (ขึ้นกับอุณหภูมิ+ขนาดบด)",
            ]
        else:
            time_steps += [
                "ถ้ารสยังไม่ตรง: ปรับทีละ 1 ตัวแปร (บด/อุณหภูมิ/ratio) และจดบันทึกผล",
            ]
            time_why += ["เมื่อเวลาอยู่ในโซนปกติ ตัวแปรอื่นมักเป็นตัวตัดสิน"]

        recs.append(Recommendation(
            title="เวลาสกัด = คันโยกที่มองเห็นได้ (ปรับทีละนิด แต่แม่น)",
            steps=time_steps,
            why=time_why,
            what_to_measure=["total_time_s", "dose_g", "water_g", "การเท/flow consistency"],
            confidence=0.72,
            proof_refs=proof_refs2,
        ))

        # EY block if available
        if ey is not None and p_ey is not None:
            ey_steps = [
                f"EY% ปัจจุบัน ~ {ey:.1f}%",
                "ถ้าต้องการมาตรฐานตัวเอง: ตั้งช่วง EY เป้าหมายตามเมล็ด/โปรไฟล์ แล้วปรับด้วยบด+เวลา+slurry",
                "อย่าใช้ EY เดี่ยว ๆ: ฟัง sensory ควบคู่เสมอ (แต่ EY ช่วยลดการเดา)",
            ]
            ey_why = [
                "EY เป็นตัวเลขที่ทำให้การคุยเรื่อง extraction ‘ยืนบนข้อมูล’ มากกว่าความเชื่อ",
            ]
            recs.append(Recommendation(
                title="Extraction Yield (EY) = เข็มทิศลดการมั่ว",
                steps=ey_steps,
                why=ey_why,
                what_to_measure=["tds_percent", "beverage_g", "dose_g"],
                confidence=0.93,
                proof_refs=[p_ey],
            ))

        summary = (
            "สรุปแบบ Coffee OS:\n"
            "- ระบบนี้จะไม่ ‘เดา’ ถ้าข้อมูลไม่พอ\n"
            "- ถ้ามีการวัด (slurry/TDS) ความแม่นจะพุ่งแบบก้าวกระโดด\n"
            "- แก่นคือ: ชงกาแฟ = energy + mass transfer ภายใต้ constraints"
        )

        return AnalysisReport(
            summary=summary,
            recommendations=recs,
            missing_inputs=[],
            proof_ledger=ledger.export(),
        )

    def _missing_for_brew(self, inp: BrewInputs) -> List[str]:
        missing = []
        # For “real problem solving”, require these minimal inputs:
        if inp.dose_g is None:
            missing.append("dose_g (กรัมกาแฟ)")
        if inp.water_g is None and inp.beverage_g is None:
            missing.append("water_g หรือ beverage_g (มวลน้ำ/มวลเครื่องดื่ม)")
        if inp.kettle_temp_c is None:
            missing.append("kettle_temp_c (อุณหภูมิน้ำที่ใช้จริง)")
        if inp.total_time_s is None:
            missing.append("total_time_s (เวลาสกัดทั้งหมด)")
        if inp.room_temp_c is None:
            missing.append("room_temp_c (อุณหภูมิห้อง)")
        if inp.brewer_preheated is None:
            missing.append("brewer_preheated (พรีฮีตอุปกรณ์หรือไม่ True/False)")
        # Optional but powerful:
        # slurry temp & TDS reduce guessing dramatically, but we won't demand them.
        return missing
