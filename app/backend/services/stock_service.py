from typing import Any

from backend.providers.fallback_provider import FallbackMarketDataProvider
from backend.services.alert_service import build_alerts
from backend.services.backtest_service import run_simple_backtest
from backend.services.dividend_analysis_service import analyze_dividends
from backend.services.fundamental_analysis_service import analyze_fundamentals
from backend.services.news_analysis_service import analyze_news
from backend.services.probability_service import calculate_probabilities
from backend.services.report_service import build_report
from backend.services.risk_service import analyze_risk, behavioral_warnings
from backend.services.scoring_service import calculate_global_score
from backend.services.strategic_watch_service import build_strategic_watch
from backend.services.technical_analysis_service import analyze_technical
from backend.services.valuation_service import analyze_valuation


provider = FallbackMarketDataProvider()
watchlist: set[str] = {"TTE.PA", "KO"}


def analyze_stock(ticker: str) -> dict[str, Any]:
    ticker = ticker.upper()
    profile = provider.get_stock_profile(ticker)
    prices = provider.get_price_history(ticker)
    fundamentals_raw = provider.get_fundamentals(ticker)
    dividends_raw = provider.get_dividends(ticker)
    news_raw = provider.get_news(ticker)

    technical = analyze_technical(prices)
    fundamental = analyze_fundamentals(fundamentals_raw)
    dividend = analyze_dividends(dividends_raw, fundamentals_raw)
    valuation = analyze_valuation(fundamentals_raw)
    news = analyze_news(news_raw)
    strategic_watch = build_strategic_watch(ticker, profile, news_raw, provider.get_news)
    risk = analyze_risk(profile, fundamentals_raw, dividend, technical, news)
    score = calculate_global_score(
        fundamental["fundamental_score"],
        dividend["dividend_score"],
        valuation["valuation_score"],
        technical["technical_score"],
        news["news_score"],
        risk["risk_score"],
    )
    probabilities = calculate_probabilities(technical, fundamental, dividend, valuation, news)
    warnings = behavioral_warnings(dividend, valuation)

    diagnostics = provider.diagnostics()
    if not diagnostics.get("sources") and profile.get("data_source"):
        diagnostics["sources"] = {"profile": profile["data_source"]}

    analysis: dict[str, Any] = {
        "ticker": ticker,
        "name": profile["name"],
        "price": technical["price"],
        "currency": profile["currency"],
        "scores": {
            "fundamental": fundamental["fundamental_score"],
            "dividend": dividend["dividend_score"],
            "valuation": valuation["valuation_score"],
            "technical": technical["technical_score"],
            "news": news["news_score"],
            "risk": risk["risk_score"],
            "global": score["global_score"],
        },
        "probabilities": probabilities,
        "levels": {
            "entry_zone_low": technical["entry_zone"][0],
            "entry_zone_high": technical["entry_zone"][1],
            "support": technical["support"],
            "resistance": technical["resistance"],
            "stop_loss": technical["stop_loss"],
            "target_1": technical["target_1"],
            "target_2": technical["target_2"],
        },
        "decision": score["decision"],
        "interpretation": score["interpretation"],
        "risk_level": risk["risk_level"],
        "profile": profile,
        "data_diagnostics": diagnostics,
        "behavioral_warning": warnings,
        "details": {
            "fundamental": fundamental,
            "dividend": dividend,
            "valuation": valuation,
            "technical": technical,
            "news": news,
            "strategic_watch": strategic_watch,
            "risk": risk,
        },
    }
    analysis["alerts"] = build_alerts(analysis)
    analysis["report"] = build_report(analysis)
    return analysis


def get_price_history_records(ticker: str) -> list[dict[str, Any]]:
    data = provider.get_price_history(ticker.upper()).copy()
    data["date"] = data["date"].dt.strftime("%Y-%m-%d")
    return data.to_dict(orient="records")


def get_watchlist() -> list[str]:
    return sorted(watchlist)


def add_to_watchlist(ticker: str) -> list[str]:
    watchlist.add(ticker.upper())
    return get_watchlist()


def remove_from_watchlist(ticker: str) -> list[str]:
    watchlist.discard(ticker.upper())
    return get_watchlist()


def backtest_stock(ticker: str) -> dict[str, Any]:
    return run_simple_backtest(provider.get_price_history(ticker.upper()))
