#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR Coffee OS (One-File Edition)
Physics-first + Proof-Gated Output (anti-hallucination by design)

Run:
  python asr_coffee_os_onefile.py --demo
  python asr_coffee_os_onefile.py --method pourover --dose 18 --water 300 --kettle 98 --room 26 --preheat true --time 210
  python asr_coffee_os_onefile.py --method pourover --dose 18 --water 300 --kettle 98 --room 26 --preheat true --time 210 --json
Optional:
  --alt 1200
  --tds 1.35 --beverage 285
  --slurry 92.0
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Tuple
import argparse
import json
import math
import sys


# ---------------------------
# Models
# ---------------------------

@dataclass(frozen=True)
class BrewInputs:
    method: str = "pourover"  # pourover, espresso, immersion
    dose_g: Optional[float] = None
    water_g: Optional[float] = None
    beverage_g: Optional[float] = None  # useful for immersion/espresso and for EY calc
    grind_setting: Optional[str] = None  # descriptive (e.g., "medium-fine")
    kettle_temp_c: Optional[float] = None
    room_temp_c: Optional[float] = None
    brewer_preheated: Optional[bool] = None
    bloom: Optional[bool] = None
    total_time_s: Optional[float] = None
    altitude_m: Optional[float] = None

    # measurements (optional but powerful)
    tds_percent: Optional[float] = None  # beverage TDS (%), e.g., 1.35
    slurry_temp_c: Optional[float] = None  # measured slurry temperature
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


# ---------------------------
# Proof Ledger (Anti-hallucination backbone)
# ---------------------------

@dataclass(frozen=True)
class Proof:
    id: str
    kind: str  # "equation" | "measurement" | "axiom" | "assumption"
    claim: str
    basis: str
    inputs: Dict[str, Any]
    output: Any
    notes: str = ""
    uncertainty: Optional[str] = None


class ProofLedger:
    def __init__(self) -> None:
        self._items: Dict[str, Proof] = {}
        self._n = 0

    def add(
        self,
        kind: str,
        claim: str,
        basis: str,
        inputs: Dict[str, Any],
        output: Any,
        notes: str = "",
        uncertainty: str | None = None,
    ) -> str:
        self._n += 1
        pid = f"P{self._n:04d}"
        self._items[pid] = Proof(
            id=pid,
            kind=kind,
            claim=claim,
            basis=basis,
            inputs=inputs,
            output=output,
            notes=notes,
            uncertainty=uncertainty,
        )
        return pid

    def export(self) -> Dict[str, Any]:
        return {k: asdict(v) for k, v in self._items.items()}


# ---------------------------
# First Principle Codex (non-negotiable rules)
# ---------------------------

class FirstPrincipleCodex:
    def __init__(self) -> None:
        self.axioms: Dict[str, str] = {}
        self._bootstrap()

    def _bootstrap(self) -> None:
        self.axioms["constraints"] = "Reality is bounded by constraints (energy/time/material)."
        self.axioms["energy_transfer"] = "Extraction is an energy + mass transfer problem."
        self.axioms["measurement"] = "If you cannot measure/proxy it, treat it as uncertain."
        self.axioms["causation"] = "Effects trace to root causes; avoid single-cause stories."
        self.axioms["entropy"] = "Without directed control, quality drifts."
        self.axioms["no_guessing"] = "If inputs are missing, request them; do not fabricate."

    def rules(self) -> List[str]:
        return [f"{k}: {v}" for k, v in self.axioms.items()]


# ---------------------------
# Physics Core (simple, explicit, defensible)
# ---------------------------

def clamp(x: float, a: float, b: float) -> float:
    return max(a, min(b, x))

def boiling_point_c_at_altitude(altitude_m: float) -> float:
    """
    Rule-of-thumb: boiling point decreases with altitude.
    Approx: -0.003 °C / meter (varies with pressure/weather).
    This is a planning proxy (not lab-precise).
    """
    return 100.0 - 0.003 * max(0.0, altitude_m)

def thermal_loss_estimate_c(
    kettle_temp_c: float,
    room_temp_c: float,
    brewer_preheated: bool,
    method: str = "pourover",
) -> Tuple[float, float]:
    """
    Returns (estimated_loss_c, estimated_slurry_peak_c).
    A heuristic proxy:
      - pourover loses more heat (air + brewer + paper)
      - no preheat loses more
      - room temp slightly shifts losses
    """
    m = method.strip().lower()
    base_loss = 6.5 if m == "pourover" else (4.5 if m == "immersion" else 3.5)
    preheat_penalty = 0.0 if brewer_preheated else 3.0
    room_penalty = clamp((25.0 - room_temp_c) * 0.08, -1.0, 2.0)
    loss = base_loss + preheat_penalty + room_penalty
    slurry_peak = kettle_temp_c - loss
    return loss, slurry_peak

def extraction_yield_percent(tds_percent: float, beverage_g: float, dose_g: float) -> float:
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
    m = method.strip().lower()
    if total_time_s is None:
        return "no_time_measurement"
    if m == "pourover":
        if total_time_s < 150:
            return "short_contact"
        if total_time_s > 270:
            return "long_contact"
        return "normal_contact"
    if m == "immersion":
        if total_time_s < 180:
            return "short_contact"
        if total_time_s > 360:
            return "long_contact"
        return "normal_contact"
    if m == "espresso":
        if total_time_s < 20:
            return "short_contact"
        if total_time_s > 35:
            return "long_contact"
        return "normal_contact"
    return "unknown_method"


# ---------------------------
# Engine (Proof-Gated)
# ---------------------------

class CoffeeOS:
    """
    Physics-first Coffee OS:
      - Only emits recommendations backed by proofs (axiom/equation/measurement/proxy assumption)
      - Missing critical inputs => returns what to measure next (no guessing)
    """

    def __init__(self) -> None:
        self.codex = FirstPrincipleCodex()

    def analyze_brew(self, inp: BrewInputs) -> AnalysisReport:
        ledger = ProofLedger()
        missing = self._missing_for_brew(inp)

        # Codex axiom proof: refusal by design
        p_axiom = ledger.add(
            kind="axiom",
            claim="If inputs are missing, request them; do not fabricate.",
            basis="no_guessing",
            inputs={},
            output=True,
            notes="ASR Codex: anti-hallucination gate",
        )

        if missing:
            rec = Recommendation(
                title="ต้องการข้อมูลเพิ่มเพื่อวิเคราะห์แบบไม่เดา (มั่ว≈0%)",
                steps=[
                    "กรอก/วัดตัวแปรที่ขาดตามรายการ Missing inputs",
                    "ถ้ามีเครื่องวัด TDS (refractometer) ให้ใส่ TDS% + beverage_g เพื่อคำนวณ EY%",
                    "ถ้ามี probe ให้วัด slurry_temp_c เพื่อยืนยันว่า ‘อุณหภูมิที่เมล็ดรับจริง’ เป็นเท่าไหร่",
                ],
                why=[
                    "การชงคือปัญหา energy + mass transfer; ถ้าตัวแปรหลักหาย การเดาจะพาคุณออกนอกฟิสิกส์",
                    "ระบบที่ไม่เดา จะทำให้คุณพัฒนา ‘สกิลที่ใช้ซ้ำได้’ ไม่ใช่สูตรที่ลอกกัน",
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

        # ---- 1) Boiling point vs altitude (proxy) ----
        bp = 100.0
        bp_uncertainty = None
        if inp.altitude_m is not None:
            bp = boiling_point_c_at_altitude(inp.altitude_m)
            bp_uncertainty = "rule-of-thumb; weather/pressure variation not included"

        p_bp = ledger.add(
            kind="equation" if inp.altitude_m is not None else "assumption",
            claim="Local boiling point sets a ceiling for achievable brew temperature",
            basis="boiling_point_c_at_altitude (proxy)",
            inputs={"altitude_m": inp.altitude_m},
            output=bp,
            uncertainty=bp_uncertainty if inp.altitude_m is not None else "altitude not provided; assume sea-level",
        )

        # ---- 2) Thermal loss (proxy if slurry not measured) ----
        kettle = float(inp.kettle_temp_c)
        room = float(inp.room_temp_c)
        preheated = bool(inp.brewer_preheated)

        loss_c, slurry_peak_est = thermal_loss_estimate_c(
            kettle_temp_c=kettle,
            room_temp_c=room,
            brewer_preheated=preheated,
            method=inp.method,
        )

        p_loss = ledger.add(
            kind="equation",
            claim="Slurry temperature is typically lower than kettle temperature due to thermal loss",
            basis="thermal_loss_estimate_c (heuristic proxy)",
            inputs={
                "kettle_temp_c": kettle,
                "room_temp_c": room,
                "brewer_preheated": preheated,
                "method": inp.method,
            },
            output={"loss_c": loss_c, "slurry_peak_est_c": slurry_peak_est},
            notes="Proxy model. Add slurry probe to upgrade proxy->measurement.",
            uncertainty="heuristic",
        )

        slurry_truth = inp.slurry_temp_c if inp.slurry_temp_c is not None else slurry_peak_est
        p_slurry = ledger.add(
            kind="measurement" if inp.slurry_temp_c is not None else "assumption",
            claim="Slurry temperature used for reasoning (what coffee bed actually receives)",
            basis="slurry_temp_c" if inp.slurry_temp_c is not None else "slurry_peak_est_c",
            inputs={"slurry_temp_c": inp.slurry_temp_c, "slurry_peak_est_c": slurry_peak_est},
            output=slurry_truth,
            notes="Measured beats estimated.",
            uncertainty=None if inp.slurry_temp_c is not None else "estimated",
        )

        # ---- 3) Contact time category ----
        time_tag = contact_time_hint(inp.method, inp.total_time_s)
        p_time = ledger.add(
            kind="equation",
            claim="Contact time category influences extraction tendency",
            basis="contact_time_hint",
            inputs={"method": inp.method, "total_time_s": inp.total_time_s},
            output=time_tag,
        )

        # ---- 4) EY% if measured ----
        ey = None
        p_ey = None
        if inp.tds_percent is not None and inp.beverage_g is not None and inp.dose_g is not None:
            ey = extraction_yield_percent(inp.tds_percent, inp.beverage_g, inp.dose_g)
            p_ey = ledger.add(
                kind="equation",
                claim="Extraction Yield can be computed from TDS, beverage mass, and dose",
                basis="extraction_yield_percent",
                inputs={"tds_percent": inp.tds_percent, "beverage_g": inp.beverage_g, "dose_g": inp.dose_g},
                output=ey,
            )

        # ---- Build recommendations (proof-gated) ----
        recs: List[Recommendation] = []

        # Temperature strategy: cap by boiling point
        max_possible = min(kettle, bp)
        p_cap = ledger.add(
            kind="equation",
            claim="Kettle temperature cannot exceed local boiling ceiling (practical cap)",
            basis="min(kettle_temp_c, boiling_point_c)",
            inputs={"kettle_temp_c": kettle, "boiling_point_c": bp},
            output=max_possible,
            uncertainty=bp_uncertainty,
        )

        recs.append(
            Recommendation(
                title="อุณหภูมิแบบ ASR: ปรับด้วย ‘อุณหภูมิที่เมล็ดรับจริง (slurry)’ ไม่ใช่ตัวเลขหน้ากา",
                steps=[
                    f"เพดานอุณหภูมิที่เป็นไปได้ ณ สภาพแวดล้อมนี้ ~ {max_possible:.1f}°C (ขึ้นกับความสูง/การเดือดจริง)",
                    f"จากระบบของคุณ: คาดว่า slurry peak ~ {slurry_peak_est:.1f}°C (สูญเสีย ~ {loss_c:.1f}°C)",
                    "ถ้าอยาก ‘ไม่เดา’ ให้ใช้ probe วัด slurry_temp_c แล้วชดเชย kettle temp เพื่อให้ slurry เข้าเป้าหมาย",
                    "หลักคิด: เมล็ดไม่ได้อ่านตัวเลขหน้ากา — มัน ‘รับ’ พลังงานตามสภาพจริงของระบบ",
                ],
                why=[
                    "ในฟิสิกส์: ตัวแปรที่ทำงานกับผงกาแฟจริง ๆ คือ slurry temperature + contact + flow",
                    "ตัวเลขช่วยให้คนคุยกันรู้เรื่อง แต่คุณภาพเกิดจากพลังงานที่ส่งผ่านจริงในระบบ",
                ],
                what_to_measure=[
                    "slurry_temp_c (ถ้ามี probe)",
                    "kettle_temp_c (วัดจริง ไม่เดา)",
                    "room_temp_c + brewer_preheated",
                ],
                confidence=0.78 if inp.slurry_temp_c is None else 0.90,
                proof_refs=[p_bp, p_loss, p_slurry, p_cap],
            )
        )

        # Time/grind guidance bounded by time_tag
        if time_tag == "short_contact":
            steps = [
                "ถ้ารส ‘บาง/เปรี้ยวโดด/หวานไม่มา’: เพิ่ม contact time ทีละน้อย (ช้าลงเล็กน้อย หรือบดละเอียดขึ้นเล็กน้อย)",
                "คุม ‘อย่างเดียว’ ทีละตัวแปร เพื่อเห็นเหตุ-ผลจริง",
            ]
            why = ["contact time สั้น → โอกาส under-extraction สูงขึ้น โดยเฉพาะเมล็ด density สูง/คั่วอ่อน"]
        elif time_tag == "long_contact":
            steps = [
                "ถ้ารส ‘ฝาด/ขม/แห้ง’: ลด contact time ทีละน้อย (ไหลเร็วขึ้น หรือบดหยาบขึ้นเล็กน้อย)",
                "เช็คการเท/การไหลว่ามีการสกัดเกินเฉพาะจุด (channeling) หรือไม่",
            ]
            why = ["contact time ยาว → ความเสี่ยง over-extraction เพิ่ม (ขึ้นกับอุณหภูมิ+ขนาดบด+flow)"]
        else:
            steps = [
                "ถ้ารสยังไม่ตรง: ปรับทีละ 1 ตัวแปร (บด/อุณหภูมิ/ratio) และจดบันทึกผล",
                "เป้าหมายคือสร้าง ‘ระบบ’ ที่ทำซ้ำได้ ไม่ใช่สูตรที่พึ่งดวง",
            ]
            why = ["เมื่อเวลาอยู่ในโซนปกติ ตัวแปรอื่นมักเป็นตัวตัดสิน (flow, grind, slurry, pour pattern)"]

        recs.append(
            Recommendation(
                title="เวลาสกัด = คันโยกที่มองเห็นได้ (ปรับทีละนิด แต่แม่นขึ้น)",
                steps=steps,
                why=why,
                what_to_measure=["total_time_s", "dose_g", "water_g / beverage_g", "flow consistency (จังหวะ/ความนิ่งของการเท)"],
                confidence=0.72,
                proof_refs=[p_time],
            )
        )

        # EY block if available
        if ey is not None and p_ey is not None:
            recs.append(
                Recommendation(
                    title="Extraction Yield (EY) = เข็มทิศลดการมั่ว (ตัวเลขที่ ‘ยืนบนของจริง’)",
                    steps=[
                        f"EY% ปัจจุบัน ~ {ey:.1f}%",
                        "ถ้าจะสร้างมาตรฐานตัวเอง: ตั้งช่วง EY เป้าหมายตามเมล็ด/โปรไฟล์ แล้วปรับด้วยบด+เวลา+slurry",
                        "อย่าใช้ EY เดี่ยว ๆ: ฟัง sensory ควบคู่เสมอ — แต่ EY ช่วยลดการเดาจากความรู้สึก",
                    ],
                    why=[
                        "EY ทำให้การคุยเรื่อง extraction มี ‘แกนเดียวกัน’ ระหว่างคน ไม่ต้องเถียงกันด้วยศรัทธา",
                        "เมื่อมี EY + slurry temp คุณกำลังคุม ‘เหตุ’ มากกว่าลุ้น ‘ผล’",
                    ],
                    what_to_measure=["tds_percent", "beverage_g", "dose_g"],
                    confidence=0.93,
                    proof_refs=[p_ey],
                )
            )

        summary = (
            "ASR Coffee OS Summary\n"
            "- ระบบนี้ออกแบบให้ ‘ไม่เดา’ เมื่อข้อมูลไม่พอ\n"
            "- เป้าหมายคือย้ายการตัดสินจาก ‘สูตร/ความเชื่อ’ ไปสู่ ‘พลังงาน+การถ่ายเทมวล’ ในระบบจริง\n"
            "- ถ้ามีการวัด (slurry/TDS) ความแม่นจะกระโดดทันที เพราะ Proof แข็งขึ้น"
        )

        return AnalysisReport(
            summary=summary,
            recommendations=recs,
            missing_inputs=[],
            proof_ledger=ledger.export(),
        )

    def _missing_for_brew(self, inp: BrewInputs) -> List[str]:
        missing: List[str] = []
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
        # slurry_temp_c + tds are optional but high impact; not required for base analysis
        return missing


# ---------------------------
# CLI
# ---------------------------

def parse_bool(s: Optional[str]) -> Optional[bool]:
    if s is None:
        return None
    t = s.strip().lower()
    if t in ("1", "true", "yes", "y", "t"):
        return True
    if t in ("0", "false", "no", "n", "f"):
        return False
    raise ValueError("preheat must be true/false")

def to_jsonable_report(report: AnalysisReport) -> Dict[str, Any]:
    return {
        "summary": report.summary,
        "missing_inputs": report.missing_inputs,
        "recommendations": [
            {
                "title": r.title,
                "steps": r.steps,
                "why": r.why,
                "what_to_measure": r.what_to_measure,
                "confidence": r.confidence,
                "proof_refs": r.proof_refs,
            }
            for r in report.recommendations
        ],
        "proof_ledger": report.proof_ledger,
    }

def run_demo() -> None:
    osys = CoffeeOS()

    demo_inputs = BrewInputs(
        method="pourover",
        dose_g=18,
        water_g=300,
        kettle_temp_c=98,
        room_temp_c=26,
        brewer_preheated=True,
        total_time_s=210,
        altitude_m=1200,
        # Uncomment to see higher confidence:
        # slurry_temp_c=92.0,
        # tds_percent=1.35, beverage_g=285,
    )

    report = osys.analyze_brew(demo_inputs)
    print(report.summary)
    if report.missing_inputs:
        print("\nMissing inputs:")
        for m in report.missing_inputs:
            print(f"- {m}")
    print("\nRecommendations:")
    for i, r in enumerate(report.recommendations, 1):
        print(f"\n{i}) {r.title} (confidence={r.confidence:.2f})")
        for s in r.steps:
            print(f"   - {s}")
        if r.what_to_measure:
            print("   measure:")
            for m in r.what_to_measure:
                print(f"     • {m}")
        if r.proof_refs:
            print(f"   proofs: {', '.join(r.proof_refs)}")

def main() -> None:
    p = argparse.ArgumentParser(
        prog="asr-coffee-onefile",
        description="ASR Coffee OS (One-File). Physics-first, proof-gated, anti-hallucination by design.",
    )
    p.add_argument("--demo", action="store_true", help="run demo scenario")
    p.add_argument("--json", action="store_true", help="print full JSON report")

    p.add_argument("--method", default="pourover")
    p.add_argument("--dose", type=float, default=None)
    p.add_argume
