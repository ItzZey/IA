from backend.services.math_utils import clamp


def calculate_global_score(
    fundamental_score: float,
    dividend_score: float,
    valuation_score: float,
    technical_score: float,
    news_score: float,
    risk_score: float,
) -> dict[str, float | str]:
    global_score = (
        fundamental_score * 0.30
        + dividend_score * 0.25
        + valuation_score * 0.15
        + technical_score * 0.15
        + news_score * 0.10
        + risk_score * 0.05
    )
    global_score = round(clamp(global_score), 1)
    if global_score < 40:
        interpretation = "eviter"
        decision = "Eviter / risque trop eleve"
    elif global_score < 55:
        interpretation = "faible_interet"
        decision = "Surveiller sans entree"
    elif global_score < 70:
        interpretation = "surveiller"
        decision = "Surveiller / attendre confirmation"
    elif global_score < 80:
        interpretation = "opportunite_correcte"
        decision = "Entree progressive possible uniquement si confirmation"
    elif global_score < 90:
        interpretation = "opportunite_forte"
        decision = "Opportunite forte a verifier manuellement"
    else:
        interpretation = "exceptionnelle_a_verifier"
        decision = "Signal exceptionnel, validation manuelle obligatoire"

    return {"global_score": global_score, "interpretation": interpretation, "decision": decision}
