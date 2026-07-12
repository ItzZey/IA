import pandas as pd

from backend.providers.mock_provider import MockMarketDataProvider
from backend.services.technical_analysis_service import (
    analyze_technical,
    calculate_bollinger,
    calculate_macd,
    calculate_rsi,
    moving_average,
)


def test_moving_average() -> None:
    series = pd.Series([1, 2, 3, 4, 5])
    assert moving_average(series, 3).iloc[-1] == 4


def test_rsi_is_bounded() -> None:
    series = pd.Series([10, 11, 12, 11, 13, 14, 13, 15, 16, 17, 16, 18, 19, 20, 21, 22])
    rsi = calculate_rsi(series).dropna()
    assert (rsi >= 0).all()
    assert (rsi <= 100).all()


def test_macd_columns() -> None:
    macd = calculate_macd(pd.Series(range(1, 80)))
    assert {"macd", "macd_signal", "macd_histogram"}.issubset(macd.columns)


def test_bollinger_columns() -> None:
    bollinger = calculate_bollinger(pd.Series(range(1, 80)))
    assert {"bb_middle", "bb_upper", "bb_lower"}.issubset(bollinger.columns)


def test_technical_analysis_shape() -> None:
    prices = MockMarketDataProvider().get_price_history("TTE.PA")
    result = analyze_technical(prices)
    assert 0 <= result["technical_score"] <= 100
    assert result["support"] <= result["resistance"]
    assert result["stop_loss"] < result["target_1"]
