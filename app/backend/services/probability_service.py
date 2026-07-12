from typing import Any

from backend.services.math_utils import clamp


def calculate_probabilities(
    technical: dict[str, Any],
    fundamental: dict[str, Any],
    dividend: dict[str, Any],
    valuation: dict[str, Any],
    news: dict[str, Any],
) -> dict[str, float | str]:
    base = 50.0
    base += (technical["technical_score"] - 50) * 0.22
    base += (fundamental["fundamental_score"] - 50) * 0.16
    base += (news["news_score"] - 50) * 0.12
    base += (valuation["valuation_score"] - 50) * 0.10
    if dividend.get("risk_of_dividend_cut") == "high":
        base -= 8
    elif dividend.get("risk_of_dividend_cut") == "medium":
        base -= 4

    probability_up_30d = round(clamp(base, 5, 95), 1)
    probability_up_7d = round(clamp(50 + (probability_up_30d - 50) * 0.55, 5, 95), 1)
    probability_up_90d = round(clamp(50 + (probability_up_30d - 50) * 1.25, 5, 95), 1)
    down_to_support = round(clamp(100 - probability_up_30d - 12, 5, 95), 1)
    hit_stop = round(clamp(down_to_support * 0.75, 5, 95), 1)
    hit_target_1 = round(clamp(probability_up_30d * 0.78, 5, 95), 1)
    hit_target_2 = round(clamp(probability_up_90d * 0.52, 5, 95), 1)

    confidence = "medium"
    if abs(probability_up_30d - 50) < 6:
        confidence = "low"
    elif abs(probability_up_30d - 50) > 15:
        confidence = "high"

    return {
        "up_7d": probability_up_7d,
        "up_30d": probability_up_30d,
        "up_90d": probability_up_90d,
        "down_to_support": down_to_support,
        "hit_stop": hit_stop,
        "hit_target_1": hit_target_1,
        "hit_target_2": hit_target_2,
        "confidence": confidence,
    }
