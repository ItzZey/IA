from typing import Any

from backend.services.math_utils import clamp


def analyze_fundamentals(fundamentals: dict[str, Any]) -> dict[str, Any]:
    score = 0.0
    strengths: list[str] = []
    weaknesses: list[str] = []
    risk_flags: list[str] = []

    pe = fundamentals.get("pe_ratio", 0)
    pb = fundamentals.get("pb_ratio", 0)
    sector_pe = fundamentals.get("sector_pe", pe)
    sector_pb = fundamentals.get("sector_pb", pb)
    roe = fundamentals.get("roe", 0)
    roa = fundamentals.get("roa", 0)
    roic = fundamentals.get("roic", 0)
    debt_to_equity = fundamentals.get("debt_to_equity", 99)
    current_ratio = fundamentals.get("current_ratio", 0)
    interest_coverage = fundamentals.get("interest_coverage", 0)

    if 0 < pe <= sector_pe * 1.1:
        score += 10
        strengths.append("P/E raisonnable par rapport au secteur")
    else:
        weaknesses.append("P/E superieur a la moyenne sectorielle")
        risk_flags.append("Valorisation potentiellement elevee")

    if 0 < pb <= sector_pb * 1.1:
        score += 5
        strengths.append("P/B raisonnable")
    if roe >= 12:
        score += 15
        strengths.append("ROE eleve")
    if roa > 3:
        score += 10
        strengths.append("ROA positif")
    if roic >= 8:
        score += 15
        strengths.append("ROIC solide")
    if debt_to_equity <= 0.8:
        score += 15
        strengths.append("Dette maitrisee")
    else:
        weaknesses.append("Endettement a surveiller")
        risk_flags.append("Dette elevee")
    if current_ratio > 1:
        score += 10
        strengths.append("Liquidite court terme correcte")
    if interest_coverage >= 5:
        score += 10
        strengths.append("Couverture des interets confortable")
    if fundamentals.get("revenue_growth", 0) > 0 and fundamentals.get("eps_growth", 0) > 0:
        score += 10
        strengths.append("Croissance CA/BPA positive")

    return {
        "fundamental_score": round(clamp(score), 1),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "risk_flags": risk_flags,
        "ratios": {
            "pe_ratio": pe,
            "pb_ratio": pb,
            "debt_to_equity": debt_to_equity,
            "current_ratio": current_ratio,
            "interest_coverage": interest_coverage,
            "roe": roe,
            "roa": roa,
            "roic": roic,
        },
    }
