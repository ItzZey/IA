from typing import Any

from backend.services.math_utils import clamp


DEFENSIVE_SECTORS = {"Consumer Defensive", "Healthcare", "Utilities"}


def analyze_risk(
    profile: dict[str, Any],
    fundamentals: dict[str, Any],
    dividend_analysis: dict[str, Any],
    technical_analysis: dict[str, Any],
    news_analysis: dict[str, Any],
) -> dict[str, Any]:
    score = 0.0
    risks: list[str] = []

    if fundamentals.get("debt_to_equity", 99) <= 0.8:
        score += 15
    else:
        risks.append("Dette elevee")
    if dividend_analysis.get("payout_ratio", 999) <= 60:
        score += 15
    else:
        risks.append("Payout ratio eleve")
    if technical_analysis.get("rsi", 50) <= 70:
        score += 10
    else:
        risks.append("Risque de surachat technique")
    if profile.get("sector") in DEFENSIVE_SECTORS:
        score += 10
    else:
        score += 5
        risks.append("Secteur potentiellement cyclique")
    score += 20
    if not news_analysis.get("risks"):
        score += 10
    else:
        risks.extend(news_analysis["risks"])
    score += 10
    if fundamentals.get("pe_ratio", 0) <= fundamentals.get("sector_pe", 999):
        score += 10
    else:
        risks.append("Valorisation a surveiller")

    risk_score = round(clamp(score), 1)
    level = "Faible" if risk_score >= 75 else "Moyen" if risk_score >= 55 else "Eleve"
    return {"risk_score": risk_score, "risk_level": level, "risks": risks}


def behavioral_warnings(dividend_analysis: dict[str, Any], valuation_analysis: dict[str, Any]) -> list[str]:
    warnings = [
        "Verifier les informations contradictoires avant toute decision.",
        "Comparer avec au moins 3 entreprises du meme secteur.",
    ]
    if dividend_analysis.get("dividend_yield", 0) > 6:
        warnings.append("Un rendement eleve peut provenir d'une forte baisse du cours.")
    if dividend_analysis.get("payout_ratio", 0) > 60:
        warnings.append("Verifier que le payout ratio reste soutenable.")
    if valuation_analysis.get("status") == "expensive":
        warnings.append("La valorisation peut limiter le potentiel de hausse.")
    return warnings
