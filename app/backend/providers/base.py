from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class MarketDataProvider(ABC):
    @abstractmethod
    def get_stock_profile(self, ticker: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_price_history(self, ticker: str) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def get_fundamentals(self, ticker: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_dividends(self, ticker: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_news(self, ticker: str) -> list[dict[str, Any]]:
        raise NotImplementedError
