from typing import Any

import pandas as pd

from backend.services.math_utils import clamp


def moving_average(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


def calculate_macd(close: pd.Series) -> pd.DataFrame:
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    return pd.DataFrame({"macd": macd, "macd_signal": signal, "macd_histogram": macd - signal})


def calculate_bollinger(close: pd.Series, window: int = 20) -> pd.DataFrame:
    middle = moving_average(close, window)
    std = close.rolling(window).std()
    return pd.DataFrame({"bb_middle": middle, "bb_upper": middle + 2 * std, "bb_lower": middle - 2 * std})


def calculate_atr(price_data: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = price_data["high"] - price_data["low"]
    high_close = (price_data["high"] - price_data["close"].shift()).abs()
    low_close = (price_data["low"] - price_data["close"].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(period).mean()


def analyze_technical(price_data: pd.DataFrame) -> dict[str, Any]:
    data = price_data.copy().sort_values("date")
    close = data["close"]
    data["ma20"] = moving_average(close, 20)
    data["ma50"] = moving_average(close, 50)
    data["ma200"] = moving_average(close, 200)
    data["rsi"] = calculate_rsi(close)
    data = pd.concat([data, calculate_macd(close), calculate_bollinger(close)], axis=1)
    data["atr"] = calculate_atr(data)
    data["volume_ma20"] = moving_average(data["volume"], 20)

    latest = data.iloc[-1]
    recent = data.tail(60)
    support = float(recent["low"].min())
    resistance = float(recent["high"].max())
    price = float(latest["close"])
    atr = float(latest["atr"]) if pd.notna(latest["atr"]) else price * 0.03
    rsi = float(latest["rsi"]) if pd.notna(latest["rsi"]) else 50

    score = 0.0
    strengths: list[str] = []
    warnings: list[str] = []

    if price > latest["ma200"]:
        score += 15
        strengths.append("Prix au-dessus de la moyenne mobile 200 jours")
    if latest["ma20"] > latest["ma50"]:
        score += 10
        strengths.append("Moyenne mobile 20 jours superieure a la 50 jours")
    if latest["ma50"] > latest["ma200"]:
        score += 10
        strengths.append("Tendance moyen terme constructive")
    if 40 <= rsi <= 65:
        score += 15
        strengths.append("RSI en zone neutre constructive")
    elif rsi < 30:
        score += 5
        warnings.append("RSI survendu, signal de rebond a confirmer")
    elif rsi > 75:
        score -= 10
        warnings.append("RSI en surachat")

    if (price - support) / price <= 0.05:
        score += 15
        strengths.append("Prix proche d'un support recent")
    if price > resistance * 0.995 and latest["volume"] > latest["volume_ma20"]:
        score += 20
        strengths.append("Cassure potentielle avec volume")
    if latest["volume"] > latest["volume_ma20"]:
        score += 10
        strengths.append("Volume superieur a la moyenne 20 jours")
    if latest["macd"] > latest["macd_signal"]:
        score += 10
        strengths.append("MACD positif")
    if price > latest["bb_upper"]:
        score -= 5
        warnings.append("Prix au-dessus de la bande de Bollinger haute")

    entry_low = round(max(support, price - atr), 2)
    entry_high = round(min(price, support + atr), 2)
    if entry_low > entry_high:
        entry_low, entry_high = round(price - atr, 2), round(price, 2)

    trend = "bullish_medium_term" if price > latest["ma200"] and latest["ma50"] > latest["ma200"] else "neutral"

    return {
        "technical_score": round(clamp(score), 1),
        "trend": trend,
        "price": round(price, 2),
        "rsi": round(rsi, 1),
        "macd": round(float(latest["macd"]), 3),
        "support": round(support, 2),
        "resistance": round(resistance, 2),
        "entry_zone": [entry_low, entry_high],
        "stop_loss": round(support - atr, 2),
        "target_1": round(resistance, 2),
        "target_2": round(resistance + (resistance - support) * 0.5, 2),
        "ma20": round(float(latest["ma20"]), 2),
        "ma50": round(float(latest["ma50"]), 2),
        "ma200": round(float(latest["ma200"]), 2),
        "strengths": strengths,
        "warnings": warnings,
        "comment": "Analyse technique utilisee uniquement pour affiner le timing.",
    }
