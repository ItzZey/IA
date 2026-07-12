from backend.services.dividend_analysis_service import analyze_dividends


def test_dividend_score_and_yield() -> None:
    result = analyze_dividends(
        {
            "dividend_yield": 4.1,
            "payout_ratio": 48,
            "dividend_growth_3y": 5,
            "dividend_growth_5y": 6,
            "consecutive_growth_years": 10,
            "payment_history_years": 20,
            "free_cash_flow_coverage": 1.8,
        },
        {"free_cash_flow": 100},
    )
    assert result["dividend_score"] >= 80
    assert result["risk_of_dividend_cut"] == "low"


def test_dangerous_payout_ratio() -> None:
    result = analyze_dividends({"dividend_yield": 9, "payout_ratio": 95})
    assert result["risk_of_dividend_cut"] == "high"
    assert any("Payout ratio" in flag for flag in result["red_flags"])
