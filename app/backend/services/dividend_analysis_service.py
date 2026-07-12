from typing import Any

from backend.services.math_utils import clamp


def analyze_dividends(dividends: dict[str, Any], fundamentals: dict[str, Any] | None = None) -> dict[str, Any]:
    fundamentals = fundamentals or {}
    score = 0.0
    strengths: list[str] = []
    red_flags: list[str] = []

    dividend_yield = dividends.get("dividend_yield", 0)
    payout_ratio = dividends.get("payout_ratio", 999)
    growth_3y = dividends.get("dividend_growth_3y", 0)
    growth_5y = dividends.get("dividend_growth_5y", 0)
    consecutive_years = dividends.get("consecutive_growth_years", 0)
    history_years = dividends.get("payment_history_years", 0)
    fcf_coverage = dividends.get("free_cash_flow_coverage", 0)

    if 2 <= dividend_yield <= 6:
        score += 15
        strengths.append("Rendement du dividende raisonnable")
    elif dividend_yield > 8:
        red_flags.append("Rendement anormalement eleve, risque de piege a rendement")

    if 30 <= payout_ratio <= 60:
        score += 25
        strengths.append("Payout ratio soutenable")
    elif payout_ratio > 80:
        red_flags.append("Payout ratio superieur a 80 %")
    elif payout_ratio > 60:
        red_flags.append("Payout ratio superieur a 60 %, a examiner avec prudence")

    if growth_3y > 0:
        score += 15
        strengths.append("Croissance du dividende positive sur 3 ans")
    if growth_5y > 0:
        score += 15
        strengths.append("Croissance du dividende positive sur 5 ans")
    if history_years >= 10:
        score += 10
        strengths.append("Historique de paiement long")
    if consecutive_years >= 5:
        score += 10
        strengths.append("Annees consecutives de hausse")
    if fcf_coverage >= 1.2 and fundamentals.get("free_cash_flow", 0) > 0:
        score += 10
        strengths.append("Free cash-flow suffisant")
    else:
        red_flags.append("Couverture par le free cash-flow a verifier")

    risk = "low"
    if len(red_flags) >= 2:
        risk = "high"
    elif red_flags:
        risk = "medium"

    return {
        "dividend_score": round(clamp(score), 1),
        "dividend_yield": dividend_yield,
        "payout_ratio": payout_ratio,
        "dividend_growth_1y": dividends.get("dividend_growth_1y", 0),
        "dividend_growth_3y": growth_3y,
        "dividend_growth_5y": growth_5y,
        "consecutive_growth_years": consecutive_years,
        "risk_of_dividend_cut": risk,
        "strengths": strengths,
        "red_flags": red_flags,
        "comment": "Dividende analyse selon rendement, payout ratio, croissance, regularite et free cash-flow.",
    }
