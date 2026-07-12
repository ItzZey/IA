from datetime import datetime
from typing import Any

import pandas as pd
import yfinance as yf

from backend.providers.base import MarketDataProvider


class ProviderDataError(RuntimeError):
    pass


def _clean_number(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    try:
        return not pd.isna(value)
    except TypeError:
        return True


def _percentage(value: Any) -> float:
    number = _clean_number(value)
    if abs(number) <= 1:
        return round(number * 100, 2)
    return round(number, 2)


def _growth_percent(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round(((current - previous) / abs(previous)) * 100, 2)


def _sentiment_from_text(text: str) -> float:
    text = text.lower()
    positive = [
        "beat",
        "beats",
        "growth",
        "raise",
        "raised",
        "increase",
        "strong",
        "record",
        "profit",
        "upgrade",
        "higher",
        "surge",
    ]
    negative = [
        "miss",
        "cuts",
        "cut",
        "fall",
        "lower",
        "decline",
        "lawsuit",
        "risk",
        "warning",
        "downgrade",
        "weak",
        "loss",
    ]
    score = sum(12 for word in positive if word in text) - sum(14 for word in negative if word in text)
    return max(-100, min(100, score))


class YFinanceMarketDataProvider(MarketDataProvider):
    def _ticker(self, ticker: str) -> yf.Ticker:
        return yf.Ticker(ticker.upper())

    def _info(self, ticker: str) -> dict[str, Any]:
        info = self._ticker(ticker).get_info()
        if not info:
            raise ProviderDataError(f"No profile data found for {ticker}")
        return info

    def get_stock_profile(self, ticker: str) -> dict[str, Any]:
        info = self._info(ticker)
        return {
            "ticker": ticker.upper(),
            "name": info.get("shortName") or info.get("longName") or ticker.upper(),
            "exchange": info.get("exchange") or info.get("fullExchangeName") or "",
            "currency": info.get("currency") or "USD",
            "sector": info.get("sector") or "Unknown",
            "industry": info.get("industry") or "Unknown",
            "country": info.get("country") or "",
            "data_source": "yfinance",
        }

    def get_price_history(self, ticker: str) -> pd.DataFrame:
        history = self._ticker(ticker).history(period="1y", interval="1d", auto_adjust=False)
        if history.empty:
            raise ProviderDataError(f"No price history found for {ticker}")
        history = history.reset_index()
        date_col = "Date" if "Date" in history.columns else "Datetime"
        data = pd.DataFrame({
            "date": pd.to_datetime(history[date_col]).dt.tz_localize(None),
            "open": history["Open"].astype(float),
            "high": history["High"].astype(float),
            "low": history["Low"].astype(float),
            "close": history["Close"].astype(float),
            "adjusted_close": history.get("Adj Close", history["Close"]).astype(float),
            "volume": history["Volume"].fillna(0).astype("int64"),
        })
        return data.dropna(subset=["open", "high", "low", "close"])

    def get_fundamentals(self, ticker: str) -> dict[str, Any]:
        stock = self._ticker(ticker)
        info = stock.get_info()
        financials = stock.financials
        cashflow = stock.cashflow

        revenue_growth = _percentage(info.get("revenueGrowth"))
        eps_growth = _percentage(info.get("earningsGrowth"))
        fcf_growth = 0.0
        free_cash_flow = _clean_number(info.get("freeCashflow"))

        if cashflow is not None and not cashflow.empty:
            fcf_row = None
            for candidate in ["Free Cash Flow", "FreeCashFlow", "Total Cash From Operating Activities"]:
                if candidate in cashflow.index:
                    fcf_row = cashflow.loc[candidate].dropna()
                    break
            if fcf_row is not None and len(fcf_row) >= 2:
                free_cash_flow = _clean_number(fcf_row.iloc[0], free_cash_flow)
                fcf_growth = _growth_percent(_clean_number(fcf_row.iloc[0]), _clean_number(fcf_row.iloc[1]))

        earnings_stability = 0.5
        if financials is not None and not financials.empty and "Net Income" in financials.index:
            income = financials.loc["Net Income"].dropna().astype(float)
            if len(income) >= 3 and income.mean() != 0:
                earnings_stability = max(0.0, min(1.0, 1 - abs(income.std() / income.mean())))

        debt_to_equity = 99.0
        if _has_value(info.get("debtToEquity")):
            debt_to_equity = _clean_number(info.get("debtToEquity")) / 100

        interest_coverage = 0.0
        ebitda = _clean_number(info.get("ebitda"))
        interest_expense = abs(_clean_number(info.get("interestExpense")))
        if ebitda > 0 and interest_expense > 0:
            interest_coverage = ebitda / interest_expense
        elif ebitda > 0 and financials is not None and not financials.empty:
            for candidate in ["Interest Expense", "InterestExpense"]:
                if candidate in financials.index:
                    values = financials.loc[candidate].dropna()
                    if len(values) > 0 and abs(_clean_number(values.iloc[0])) > 0:
                        interest_coverage = ebitda / abs(_clean_number(values.iloc[0]))
                    break

        return {
            "revenue_growth": revenue_growth,
            "eps_growth": eps_growth,
            "fcf_growth": fcf_growth,
            "earnings_stability": round(earnings_stability, 2),
            "pe_ratio": _clean_number(info.get("trailingPE") or info.get("forwardPE")),
            "pb_ratio": _clean_number(info.get("priceToBook")),
            "debt_to_equity": debt_to_equity,
            "current_ratio": _clean_number(info.get("currentRatio")),
            "interest_coverage": interest_coverage,
            "roe": _percentage(info.get("returnOnEquity")),
            "roa": _percentage(info.get("returnOnAssets")),
            "roic": _percentage(info.get("returnOnCapital")),
            "free_cash_flow": free_cash_flow,
            "sector_pe": _clean_number(info.get("forwardPE") or info.get("trailingPE"), 15),
            "sector_pb": _clean_number(info.get("priceToBook"), 2),
        }

    def get_dividends(self, ticker: str) -> dict[str, Any]:
        stock = self._ticker(ticker)
        info = stock.get_info()
        dividends = stock.dividends
        current_yield = _percentage(info.get("dividendYield") or info.get("trailingAnnualDividendYield"))
        payout_ratio = _percentage(info.get("payoutRatio"))
        payment_history_years = 0
        consecutive_growth_years = 0
        growth_1y = 0.0
        growth_3y = 0.0
        growth_5y = 0.0
        regularity = 0.0

        if dividends is not None and not dividends.empty:
            dividends.index = pd.to_datetime(dividends.index).tz_localize(None)
            annual = dividends.groupby(dividends.index.year).sum().sort_index()
            annual = annual[annual > 0]
            payment_history_years = int(len(annual))
            regularity = round(min(1.0, len(dividends.tail(20)) / 20), 2)
            if len(annual) >= 2:
                growth_1y = _growth_percent(float(annual.iloc[-1]), float(annual.iloc[-2]))
            if len(annual) >= 4:
                growth_3y = _growth_percent(float(annual.iloc[-1]), float(annual.iloc[-4])) / 3
            if len(annual) >= 6:
                growth_5y = _growth_percent(float(annual.iloc[-1]), float(annual.iloc[-6])) / 5
            for idx in range(len(annual) - 1, 0, -1):
                if annual.iloc[idx] > annual.iloc[idx - 1]:
                    consecutive_growth_years += 1
                else:
                    break

        fcf_coverage = 0.0
        total_cash = _clean_number(info.get("totalCash"))
        dividend_rate = _clean_number(info.get("dividendRate"))
        shares = _clean_number(info.get("sharesOutstanding"))
        total_dividend_estimate = dividend_rate * shares
        free_cash_flow = _clean_number(info.get("freeCashflow"))
        if total_dividend_estimate > 0 and free_cash_flow > 0:
            fcf_coverage = round(free_cash_flow / total_dividend_estimate, 2)
        elif total_cash > 0 and total_dividend_estimate > 0:
            fcf_coverage = round(total_cash / total_dividend_estimate, 2)

        return {
            "dividend_yield": current_yield,
            "payout_ratio": payout_ratio,
            "dividend_growth_1y": round(growth_1y, 2),
            "dividend_growth_3y": round(growth_3y, 2),
            "dividend_growth_5y": round(growth_5y, 2),
            "consecutive_growth_years": consecutive_growth_years,
            "payment_history_years": payment_history_years,
            "regularity": regularity,
            "free_cash_flow_coverage": fcf_coverage,
        }

    def get_news(self, ticker: str) -> list[dict[str, Any]]:
        items = self._ticker(ticker).news or []
        output: list[dict[str, Any]] = []
        for item in items[:10]:
            content = item.get("content", item)
            title = content.get("title", "")
            summary = content.get("summary") or content.get("description") or ""
            text = f"{title} {summary}"
            provider = content.get("provider", {})
            published = content.get("pubDate") or content.get("displayTime")
            output.append({
                "title": title or "Actualite sans titre",
                "source": provider.get("displayName") if isinstance(provider, dict) else "",
                "url": (content.get("canonicalUrl") or content.get("clickThroughUrl") or {}).get("url", ""),
                "published_at": published or datetime.utcnow().isoformat(),
                "summary": summary,
                "sentiment_score": _sentiment_from_text(text),
                "impact_score": 55 if summary else 35,
            })
        return output
