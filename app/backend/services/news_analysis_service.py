from typing import Any

from backend.services.math_utils import clamp


def analyze_news(news_items: list[dict[str, Any]]) -> dict[str, Any]:
    if not news_items:
        return {"news_score": 50, "sentiment": "neutral", "major_events": [], "risks": []}

    weighted = 0.0
    total_impact = 0.0
    major_events: list[str] = []
    risks: list[str] = []
    for item in news_items:
        sentiment = float(item.get("sentiment_score", 0))
        impact = float(item.get("impact_score", 10))
        weighted += sentiment * impact
        total_impact += impact
        if impact >= 60 and sentiment >= 0:
            major_events.append(item.get("title", "Evenement positif important"))
        if impact >= 50 and sentiment < 0:
            risks.append(item.get("title", "Risque d'actualite"))

    sentiment_score = weighted / total_impact if total_impact else 0
    news_score = clamp(50 + sentiment_score / 2)
    label = "neutral"
    if sentiment_score >= 60:
        label = "very_positive"
    elif sentiment_score >= 20:
        label = "positive"
    elif sentiment_score <= -60:
        label = "very_negative"
    elif sentiment_score <= -20:
        label = "negative"
    elif sentiment_score > 0:
        label = "neutral_positive"

    return {
        "news_score": round(news_score, 1),
        "sentiment_score": round(sentiment_score, 1),
        "sentiment": label,
        "major_events": major_events,
        "risks": risks,
    }
