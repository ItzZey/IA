from backend.services.strategic_watch_service import build_strategic_watch


def test_strategic_watch_builds_sector_watch() -> None:
    profile = {"sector": "Energy"}
    company_news = [
        {
            "title": "Company raises dividend after strong cash flow",
            "summary": "Dividend and free cash flow improved.",
            "sentiment_score": 35,
            "impact_score": 70,
        },
        {
            "title": "Regulation risk and new energy tax warning",
            "summary": "Analysts warn about tax and regulation pressure.",
            "sentiment_score": -30,
            "impact_score": 65,
        },
    ]

    def fetch_news(ticker: str):
        return [
            {
                "title": f"{ticker} oil market risk",
                "summary": "Brent and OPEC headlines create macro risk.",
                "sentiment_score": -10,
                "impact_score": 50,
            }
        ]

    result = build_strategic_watch("TTE.PA", profile, company_news, fetch_news)

    assert result["sector"] == "Energy"
    assert result["watched_sources"]["TTE.PA"] == "entreprise"
    assert "SHEL" in result["watched_sources"]
    assert result["risks"]
    assert result["opportunities"]
    assert result["dividend_alerts"]
