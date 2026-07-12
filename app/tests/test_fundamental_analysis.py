from backend.services.fundamental_analysis_service import analyze_fundamentals


def test_fundamental_score() -> None:
    result = analyze_fundamentals(
        {
            "pe_ratio": 10,
            "pb_ratio": 1.2,
            "sector_pe": 14,
            "sector_pb": 2,
            "roe": 18,
            "roa": 7,
            "roic": 12,
            "debt_to_equity": 0.4,
            "current_ratio": 1.2,
            "interest_coverage": 8,
            "revenue_growth": 4,
            "eps_growth": 5,
        }
    )
    assert result["fundamental_score"] == 100
    assert "Dette maitrisee" in result["strengths"]
