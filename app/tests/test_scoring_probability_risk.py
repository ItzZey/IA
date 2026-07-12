from backend.services.probability_service import calculate_probabilities
from backend.services.risk_service import analyze_risk
from backend.services.scoring_service import calculate_global_score


def test_global_score_weighting() -> None:
    result = calculate_global_score(80, 80, 60, 60, 50, 70)
    assert result["global_score"] == 70.5
    assert "decision" in result


def test_probability_bounded_between_5_and_95() -> None:
    result = calculate_probabilities(
        {"technical_score": 100},
        {"fundamental_score": 100},
        {"dividend_score": 100, "risk_of_dividend_cut": "low"},
        {"valuation_score": 100},
        {"news_score": 100},
    )
    assert 5 <= result["up_30d"] <= 95
    assert 5 <= result["hit_stop"] <= 95


def test_risk_detects_payout_and_sector() -> None:
    result = analyze_risk(
        {"sector": "Energy"},
        {"debt_to_equity": 1.2, "pe_ratio": 20, "sector_pe": 15},
        {"payout_ratio": 90},
        {"rsi": 80},
        {"risks": ["News negative"]},
    )
    assert result["risk_score"] < 60
    assert "Payout ratio eleve" in result["risks"]
