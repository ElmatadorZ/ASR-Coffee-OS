from __future__ import annotations
import json
import argparse
from .models import BrewInputs
from .engine import CoffeeOS


def main() -> None:
    p = argparse.ArgumentParser(prog="asr-coffee", description="ASR Coffee OS (Physics-first, proof-gated).")
    p.add_argument("--method", default="pourover")
    p.add_argument("--dose", type=float, default=None)
    p.add_argument("--water", type=float, default=None)
    p.add_argument("--beverage", type=float, default=None)
    p.add_argument("--kettle", type=float, default=None)
    p.add_argument("--room", type=float, default=None)
    p.add_argument("--preheat", type=str, default=None, help="true/false")
    p.add_argument("--time", type=float, default=None)
    p.add_argument("--alt", type=float, default=None)
    p.add_argument("--tds", type=float, default=None)
    p.add_argument("--slurry", type=float, default=None)
    p.add_argument("--json", action="store_true", help="print full JSON report")

    args = p.parse_args()

    pre = None
    if args.preheat is not None:
        pre = args.preheat.strip().lower() in ["1", "true", "yes", "y"]

    osys = CoffeeOS()
    report = osys.analyze_brew(BrewInputs(
        method=args.method,
        dose_g=args.dose,
        water_g=args.water,
        beverage_g=args.beverage,
        kettle_temp_c=args.kettle,
        room_temp_c=args.room,
        brewer_preheated=pre,
        total_time_s=args.time,
        altitude_m=args.alt,
        tds_percent=args.tds,
        slurry_temp_c=args.slurry,
    ))

    if args.json:
        print(json.dumps({
            "summary": report.summary,
            "missing_inputs": report.missing_inputs,
            "recommendations": [r.__dict__ for r in report.recommendations],
            "proof_ledger": report.proof_ledger,
        }, ensure_ascii=False, indent=2))
        return

    print(report.summary)
    if report.missing_inputs:
        print("\nMissing inputs:")
        for x in report.missing_inputs:
            print(f"- {x}")
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
