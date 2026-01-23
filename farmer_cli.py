from __future__ import annotations
import argparse, json
from .farmer_models import FarmContext, CherryLot, FermentationPlan, FermentationLog, DryingPlan
from .farmer_agent import FarmerModeAgent


def main() -> None:
    p = argparse.ArgumentParser(prog="asr-farmer", description="ASR Farmer Mode (proof-gated)")
    p.add_argument("--lot", required=True)
    p.add_argument("--harvest_date", required=True)
    p.add_argument("--brix", type=float, default=None)
    p.add_argument("--ripeness", type=float, default=None)
    p.add_argument("--floaters", type=float, default=None)

    p.add_argument("--target_temp", type=float, default=None)
    p.add_argument("--target_hours", type=float, default=None)
    p.add_argument("--process", default="anaerobic_natural")

    p.add_argument("--dry", default="raised_bed")
    p.add_argument("--json", action="store_true")

    args = p.parse_args()

    agent = FarmerModeAgent()

    farm = FarmContext()
    lot = CherryLot(
        lot_id=args.lot,
        harvest_date=args.harvest_date,
        brix=args.brix,
        ripeness_percent=args.ripeness,
        floaters_percent=args.floaters,
    )
    ferm_plan = FermentationPlan(
        process=args.process,
        target_profile="red_berry",
        target_temp_c=args.target_temp,
        target_hours=args.target_hours,
        oxygen_control="sealed",
    )
    logs = []  # can extend later with CSV input
    dry_plan = DryingPlan(method=args.dry)

    report = agent.run(farm, lot, ferm_plan, logs, dry_plan)

    if args.json:
        print(json.dumps(report.__dict__, ensure_ascii=False, indent=2))
        return

    print(report.summary)
    print("\nACTION NOW:")
    for a in report.action_now:
        print("-", a)
    print("\nRISKS:")
    for r in report.risks:
        print("-", r)
    print("\nMEASURE NEXT:")
    for m in report.what_to_measure_next:
        print("-", m)
    print("\nSOP:")
    for s in report.SOP:
        print("-", s)
