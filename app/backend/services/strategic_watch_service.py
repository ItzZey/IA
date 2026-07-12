from collections.abc import Callable
from typing import Any

from backend.services.math_utils import clamp
from backend.services.translation_service import translate_label, translate_to_french


NewsFetcher = Callable[[str], list[dict[str, Any]]]


SECTOR_WATCHLISTS: dict[str, dict[str, Any]] = {
    "energy": {
        "competitors": ["SHEL", "BP", "XOM", "CVX", "ENI.MI"],
        "macro": ["CL=F", "BZ=F", "NG=F", "XLE"],
        "themes": [
            "Brent / WTI",
            "OPEP",
            "prix du gaz",
            "geopolitique",
            "raffinage",
            "transition energetique",
            "taxes energie",
            "sanctions",
            "capex",
            "free cash-flow",
        ],
    },
    "consumer defensive": {
        "competitors": ["PEP", "KDP", "MDLZ", "MNST"],
        "macro": ["XLP", "DX-Y.NYB"],
        "themes": ["inflation", "marges", "volumes", "devises", "pouvoir de fixation des prix"],
    },
    "technology": {
        "competitors": ["MSFT", "GOOGL", "META", "NVDA"],
        "macro": ["XLK", "^IXIC"],
        "themes": ["IA", "cloud", "semi-conducteurs", "reglementation", "capex"],
    },
    "healthcare": {
        "competitors": ["JNJ", "PFE", "MRK", "NVS"],
        "macro": ["XLV"],
        "themes": ["FDA", "brevets", "pipeline", "prix medicaments", "litiges"],
    },
}

DEFAULT_WATCHLIST = {
    "competitors": ["SPY", "VGK"],
    "macro": ["^GSPC", "^STOXX50E", "DX-Y.NYB"],
    "themes": ["taux", "inflation", "croissance", "devises", "reglementation"],
}

RISK_KEYWORDS = {
    "cut": 18,
    "cuts": 18,
    "downgrade": 16,
    "lawsuit": 18,
    "fine": 14,
    "sanction": 18,
    "warning": 14,
    "miss": 14,
    "weak": 12,
    "decline": 12,
    "fall": 10,
    "debt": 10,
    "strike": 12,
    "accident": 18,
    "spill": 18,
    "tax": 10,
    "regulation": 12,
}

OPPORTUNITY_KEYWORDS = {
    "beat": 16,
    "beats": 16,
    "upgrade": 16,
    "raise": 14,
    "raised": 14,
    "growth": 10,
    "record": 12,
    "strong": 10,
    "buyback": 14,
    "dividend": 12,
    "cash flow": 14,
    "deal": 8,
    "approval": 10,
}

DIVIDEND_KEYWORDS = {"dividend", "payout", "distribution", "buyback", "free cash flow", "cash flow"}
MACRO_KEYWORDS = {"rate", "rates", "inflation", "brent", "wti", "oil", "gas", "opec", "currency", "dollar"}


def _sector_config(profile: dict[str, Any]) -> dict[str, Any]:
    sector = str(profile.get("sector", "")).lower()
    for key, config in SECTOR_WATCHLISTS.items():
        if key in sector:
            return config
    return DEFAULT_WATCHLIST


def _text(item: dict[str, Any]) -> str:
    return f"{item.get('title', '')} {item.get('summary', '')}".lower()


def _keyword_score(text: str, keywords: dict[str, int]) -> int:
    return sum(weight for keyword, weight in keywords.items() if keyword in text)


def _dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in items:
        title = item.get("title", "").strip().lower()
        if not title or title in seen:
            continue
        seen.add(title)
        unique.append(item)
    return unique


def _summarize_item(item: dict[str, Any], scope: str, ticker: str) -> dict[str, Any]:
    text = _text(item)
    risk_points = _keyword_score(text, RISK_KEYWORDS)
    opportunity_points = _keyword_score(text, OPPORTUNITY_KEYWORDS)
    dividend_relevance = any(keyword in text for keyword in DIVIDEND_KEYWORDS)
    macro_relevance = any(keyword in text for keyword in MACRO_KEYWORDS)
    sentiment = float(item.get("sentiment_score", 0))
    impact = float(item.get("impact_score", 35))
    risk_score = risk_points + max(0, -sentiment) * 0.3
    opportunity_score = opportunity_points + max(0, sentiment) * 0.25
    importance = clamp(impact + risk_score + opportunity_score, 0, 100)

    if risk_score >= opportunity_score and risk_score >= 10:
        classification = "risk"
    elif opportunity_score > risk_score and opportunity_score >= 10:
        classification = "opportunity"
    else:
        classification = "watch"

    return {
        "scope": scope,
        "ticker": ticker,
        "title": translate_to_french(item.get("title", "Actualite sans titre")),
        "original_title": item.get("title", "Actualite sans titre"),
        "source": item.get("source", ""),
        "published_at": item.get("published_at", ""),
        "url": item.get("url", ""),
        "summary": translate_to_french(item.get("summary", "")),
        "original_summary": item.get("summary", ""),
        "classification": classification,
        "classification_label": translate_label(classification),
        "importance": round(importance, 1),
        "risk_points": round(risk_score, 1),
        "opportunity_points": round(opportunity_score, 1),
        "dividend_relevance": dividend_relevance,
        "macro_relevance": macro_relevance,
    }


def build_strategic_watch(
    ticker: str,
    profile: dict[str, Any],
    company_news: list[dict[str, Any]],
    fetch_news: NewsFetcher,
) -> dict[str, Any]:
    config = _sector_config(profile)
    competitors = [item for item in config["competitors"] if item.upper() != ticker.upper()][:5]
    macro_tickers = config["macro"][:4]

    raw_items: list[dict[str, Any]] = []
    for item in company_news:
        raw_items.append(_summarize_item(item, "entreprise", ticker))

    watched_sources: dict[str, str] = {ticker: "entreprise"}
    errors: dict[str, str] = {}

    for related_ticker in competitors:
        watched_sources[related_ticker] = "concurrent"
        try:
            for item in fetch_news(related_ticker)[:5]:
                raw_items.append(_summarize_item(item, "concurrent", related_ticker))
        except Exception as exc:  # noqa: BLE001 - watch must stay resilient
            errors[related_ticker] = str(exc)

    for macro_ticker in macro_tickers:
        watched_sources[macro_ticker] = "macro/secteur"
        try:
            for item in fetch_news(macro_ticker)[:5]:
                raw_items.append(_summarize_item(item, "macro/secteur", macro_ticker))
        except Exception as exc:  # noqa: BLE001
            errors[macro_ticker] = str(exc)

    items = sorted(_dedupe(raw_items), key=lambda item: item["importance"], reverse=True)[:18]
    risks = [item for item in items if item["classification"] == "risk"][:6]
    opportunities = [item for item in items if item["classification"] == "opportunity"][:6]
    watch_items = [item for item in items if item["classification"] == "watch"][:6]

    risk_pressure = sum(item["risk_points"] for item in risks)
    opportunity_pressure = sum(item["opportunity_points"] for item in opportunities)
    dividend_alerts = [item for item in items if item["dividend_relevance"]][:5]
    macro_alerts = [item for item in items if item["macro_relevance"] or item["scope"] == "macro/secteur"][:6]

    net = opportunity_pressure - risk_pressure
    if risk_pressure >= 45:
        urgency = "elevee"
    elif risk_pressure >= 20 or abs(net) >= 25:
        urgency = "moyenne"
    else:
        urgency = "faible"

    sentiment = "neutre"
    if net >= 25:
        sentiment = "positif"
    elif net <= -25:
        sentiment = "negatif"
    elif net > 5:
        sentiment = "legerement positif"
    elif net < -5:
        sentiment = "legerement negatif"

    dividend_impact = "a surveiller"
    if any(item["classification"] == "risk" for item in dividend_alerts):
        dividend_impact = "risque potentiel a verifier"
    elif any(item["classification"] == "opportunity" for item in dividend_alerts):
        dividend_impact = "plutot favorable"

    return {
        "sector": profile.get("sector", "Unknown"),
        "themes": config["themes"],
        "watched_sources": watched_sources,
        "urgency": urgency,
        "sentiment": sentiment,
        "risk_pressure": round(risk_pressure, 1),
        "opportunity_pressure": round(opportunity_pressure, 1),
        "dividend_impact": dividend_impact,
        "risks": risks,
        "opportunities": opportunities,
        "watch_items": watch_items,
        "dividend_alerts": dividend_alerts,
        "macro_alerts": macro_alerts,
        "errors": errors,
    }
