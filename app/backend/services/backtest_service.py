from typing import Any

import pandas as pd

from backend.services.technical_analysis_service import calculate_rsi, moving_average


def run_simple_backtest(price_data: pd.DataFrame) -> dict[str, Any]:
    data = price_data.copy().sort_values("date")
    data["ma200"] = moving_average(data["close"], 200)
    data["rsi"] = calculate_rsi(data["close"])
    data["signal"] = (data["close"] > data["ma200"]) & (data["rsi"].between(40, 65))
    data["daily_return"] = data["close"].pct_change().fillna(0)
    shifted_signal = data["signal"].shift(fill_value=False).astype(bool)
    data["strategy_return"] = data["daily_return"] * shifted_signal

    equity = (1 + data["strategy_return"]).cumprod()
    buy_hold = (1 + data["daily_return"]).cumprod()
    drawdown = equity / equity.cummax() - 1
    trades = int((data["signal"] & ~shifted_signal).sum())
    total_return = float(equity.iloc[-1] - 1)
    buy_hold_return = float(buy_hold.iloc[-1] - 1)
    volatility = float(data["strategy_return"].std() * (252 ** 0.5))
    sharpe = float((data["strategy_return"].mean() * 252) / volatility) if volatility else 0.0

    return {
        "total_return_pct": round(total_return * 100, 2),
        "buy_hold_return_pct": round(buy_hold_return * 100, 2),
        "annualized_volatility_pct": round(volatility * 100, 2),
        "max_drawdown_pct": round(float(drawdown.min()) * 100, 2),
        "trades": trades,
        "sharpe_ratio": round(sharpe, 2),
        "note": "Backtest simplifie base sur prix > MM200 et RSI entre 40 et 65.",
    }
