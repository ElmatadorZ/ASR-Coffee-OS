import csv
from typing import List, Dict


def read_artisan_csv(path: str) -> List[Dict[str, float]]:
    """
    Minimal Artisan CSV parser
    Returns time-series of BT, ET, ROR
    """
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "time_s": float(r["Time"]),
                "bt_c": float(r["BT"]),
                "et_c": float(r["ET"]),
                "ror": float(r.get("ROR", 0)),
            })
    return rows
