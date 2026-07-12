from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

from backend.providers.base import MarketDataProvider


class MockMarketDataProvider(MarketDataProvider):
    def get_stock_profile(self, ticker: str) -> dict[str, Any]:
        profiles = {
            "TTE.PA": {
                "ticker": "TTE.PA",
                "name": "TotalEnergies",
                "exchange": "Euronext Paris",
                "currency": "EUR",
                "sector": "Energy",
                "industry": "Integrated Oil & Gas",
                "country": "France",
            },
            "KO": {
                "ticker": "KO",
                "name": "Coca-Cola",
                "exchange": "NYSE",
                "currency": "USD",
                "sector": "Consumer Defensive",
                "industry": "Beverages",
                "country": "United States",
            },
        }
        return profiles.get(ticker.upper(), {
            "ticker": ticker.upper(),
            "name": f"{ticker.upper()} Mock Company",
            "exchange": "Mock Exchange",
            "currency": "EUR",
            "sector": "Industrials",
            "industry": "Diversified",
            "country": "France",
        })

    def get_price_history(self, ticker: str) -> pd.DataFrame:
        seed = abs(hash(ticker.upper())) % 2**32
        rng = np.random.default_rng(seed)
        days = 260
        dates = [datetime.today() - timedelta(days=days - i) for i in range(days)]
        start_price = 58.0 if ticker.upper() == "TTE.PA" else 64.0
        drift = 0.00035
        volatility = 0.012
        returns = rng.normal(drift, volatility, days)
        close = start_price * np.cumprod(1 + returns)
        high = close * (1 + rng.uniform(0.002, 0.018, days))
        low = close * (1 - rng.uniform(0.002, 0.018, days))
        open_ = close * (1 + rng.normal(0, 0.004, days))
        volume = rng.integers(1_200_000, 5_500_000, days)
        return pd.DataFrame({
            "date": pd.to_datetime(dates),
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "adjusted_close": close,
            "volume": volume,
        })

    def get_fundamentals(self, ticker: str) -> dict[str, Any]:
        return {
            "revenue_growth": 5.2,
            "eps_growth": 6.4,
            "fcf_growth": 4.8,
            "earnings_stability": 0.78,
            "pe_ratio": 9.8 if ticker.upper() == "TTE.PA" else 23.5,
            "pb_ratio": 1.2,
            "debt_to_equity": 0.48,
            "current_ratio": 1.28,
            "interest_coverage": 9.4,
            "roe": 17.8,
            "roa": 7.1,
            "roic": 12.6,
            "free_cash_flow": 18_000_000_000,
            "sector_pe": 14.0,
            "sector_pb": 1.8,
        }

    def get_dividends(self, ticker: str) -> dict[str, Any]:
        return {
            "dividend_yield": 4.1 if ticker.upper() == "TTE.PA" else 3.0,
            "payout_ratio": 48.0,
            "dividend_growth_1y": 5.1,
            "dividend_growth_3y": 4.7,
            "dividend_growth_5y": 5.9,
            "consecutive_growth_years": 18,
            "payment_history_years": 25,
            "regularity": 0.94,
            "free_cash_flow_coverage": 1.9,
        }

    def get_news(self, ticker: str) -> list[dict[str, Any]]:
        return [
            {
                "title": "Resultats trimestriels superieurs aux attentes",
                "source": "Mock Finance",
                "sentiment_score": 38,
                "impact_score": 75,
                "summary": "Croissance moderee et dividende maintenu.",
            },
            {
                "title": "Pression reglementaire sectorielle a surveiller",
                "source": "Mock Macro",
                "sentiment_score": -22,
                "impact_score": 55,
                "summary": "Le secteur reste sensible aux decisions politiques et aux taux.",
            },
        ]
