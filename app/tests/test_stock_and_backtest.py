from backend.services.backtest_service import run_simple_backtest
from backend.providers.mock_provider import MockMarketDataProvider
from backend.services.stock_service import analyze_stock


def test_full_stock_analysis_contains_expected_keys() -> None:
    result = analyze_stock("TTE.PA")
    assert result["ticker"] == "TTE.PA"
    assert "scores" in result
    assert "probabilities" in result
    assert "report" in result
    assert "Cette application fournit une analyse educative" in result["report"]


def test_backtest_returns_metrics() -> None:
    prices = MockMarketDataProvider().get_price_history("TTE.PA")
    result = run_simple_backtest(prices)
    assert "total_return_pct" in result
    assert "max_drawdown_pct" in result
    assert "sharpe_ratio" in result
