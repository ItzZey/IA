from typing import Any

import pandas as pd

from backend.providers.base import MarketDataProvider
from backend.providers.mock_provider import MockMarketDataProvider
from backend.providers.yfinance_provider import YFinanceMarketDataProvider


class FallbackMarketDataProvider(MarketDataProvider):
    def __init__(self) -> None:
        self.real = YFinanceMarketDataProvider()
        self.mock = MockMarketDataProvider()
        self.last_errors: dict[str, str] = {}
        self.last_sources: dict[str, str] = {}

    def _with_fallback(self, ticker: str, method: str) -> Any:
        try:
            value = getattr(self.real, method)(ticker)
            self.last_sources[method] = "yfinance"
            self.last_errors.pop(method, None)
            return value
        except Exception as exc:  # noqa: BLE001 - provider boundary must be resilient
            self.last_sources[method] = "mock_fallback"
            self.last_errors[method] = str(exc)
            return getattr(self.mock, method)(ticker)

    def get_stock_profile(self, ticker: str) -> dict[str, Any]:
        profile = self._with_fallback(ticker, "get_stock_profile")
        profile["data_source"] = self.last_sources.get("get_stock_profile", "unknown")
        return profile

    def get_price_history(self, ticker: str) -> pd.DataFrame:
        return self._with_fallback(ticker, "get_price_history")

    def get_fundamentals(self, ticker: str) -> dict[str, Any]:
        return self._with_fallback(ticker, "get_fundamentals")

    def get_dividends(self, ticker: str) -> dict[str, Any]:
        return self._with_fallback(ticker, "get_dividends")

    def get_news(self, ticker: str) -> list[dict[str, Any]]:
        return self._with_fallback(ticker, "get_news")

    def diagnostics(self) -> dict[str, Any]:
        return {"sources": dict(self.last_sources), "errors": dict(self.last_errors)}
