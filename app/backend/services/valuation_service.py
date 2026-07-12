from typing import Any

from backend.services.math_utils import clamp


def analyze_valuation(fundamentals: dict[str, Any]) -> dict[str, Any]:
    pe = fundamentals.get("pe_ratio", 0)
    pb = fundamentals.get("pb_ratio", 0)
    sector_pe = fundamentals.get("sector_pe", pe)
    sector_pb = fundamentals.get("sector_pb", pb)

    score = 50.0
    notes: list[str] = []
    if pe and sector_pe:
        pe_discount = (sector_pe - pe) / sector_pe
        score += pe_discount * 35
        notes.append("Comparaison P/E avec le secteur integree")
    if pb and sector_pb:
        pb_discount = (sector_pb - pb) / sector_pb
        score += pb_discount * 20
        notes.append("Comparaison P/B avec le secteur integree")

    status = "reasonable"
    if score >= 70:
        status = "attractive"
    elif score < 45:
        status = "expensive"

    return {"valuation_score": round(clamp(score), 1), "status": status, "notes": notes}
