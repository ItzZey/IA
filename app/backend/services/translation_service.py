from functools import lru_cache


STATIC_TRANSLATIONS = {
    "risk": "risque",
    "opportunity": "opportunite",
    "watch": "a surveiller",
    "macro": "macro",
    "dividend": "dividende",
    "pricing power": "pouvoir de fixation des prix",
    "cash flow": "flux de tresorerie",
    "free cash-flow": "flux de tresorerie disponible",
    "cloud": "cloud",
    "pipeline": "pipeline",
}


def translate_label(text: str) -> str:
    return STATIC_TRANSLATIONS.get(text, text)


def _looks_french(text: str) -> bool:
    lowered = text.lower()
    french_markers = [" le ", " la ", " les ", " des ", " une ", " pour ", " avec ", " marche ", " risque "]
    return any(marker in f" {lowered} " for marker in french_markers)


def _static_fallback(text: str) -> str:
    translated = text
    replacements = {
        "dividend": "dividende",
        "Dividend": "Dividende",
        "investor": "investisseur",
        "Investor": "Investisseur",
        "investors": "investisseurs",
        "stock": "action",
        "Stock": "Action",
        "stocks": "actions",
        "buy": "acheter",
        "Buy": "Acheter",
        "risk": "risque",
        "Risk": "Risque",
        "growth": "croissance",
        "Growth": "Croissance",
        "cash flow": "flux de tresorerie",
        "strong": "solide",
        "Strong": "Solide",
        "warning": "avertissement",
        "Warning": "Avertissement",
        "market": "marche",
        "Market": "Marche",
        "sales": "ventes",
        "Sales": "Ventes",
        "consumer": "consommateur",
        "Consumer": "Consommateur",
        "price": "prix",
        "Price": "Prix",
        "share": "part",
        "shares": "actions",
        "analysts": "analystes",
        "Analysts": "Analystes",
    }
    for source, target in replacements.items():
        translated = translated.replace(source, target)
    return translated


@lru_cache(maxsize=512)
def translate_to_french(text: str) -> str:
    clean = (text or "").strip()
    if not clean or _looks_french(clean):
        return clean
    if len(clean.split()) <= 3:
        return _static_fallback(clean)
    if len(clean) > 1800:
        clean = clean[:1800].rsplit(" ", 1)[0] + "..."
    try:
        from deep_translator import GoogleTranslator

        return GoogleTranslator(source="auto", target="fr").translate(clean)
    except Exception:
        return _static_fallback(clean)
