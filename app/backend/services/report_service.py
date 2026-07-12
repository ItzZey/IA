from typing import Any

from backend.config import settings


def build_report(analysis: dict[str, Any]) -> str:
    scores = analysis["scores"]
    probabilities = analysis["probabilities"]
    levels = analysis["levels"]
    fundamental = analysis["details"]["fundamental"]
    dividend = analysis["details"]["dividend"]
    technical = analysis["details"]["technical"]
    news = analysis["details"]["news"]
    sources = analysis.get("data_diagnostics", {}).get("sources", {})
    source_text = ", ".join(f"{key.replace('get_', '')}: {value}" for key, value in sources.items()) or "non renseigne"

    return f"""# Analyse de {analysis['ticker']}

## Resume
L'action presente un profil {analysis['risk_level'].lower()} avec un score global de {scores['global']}/100.
Decision systeme : {analysis['decision']}.
Sources de donnees : {source_text}.

## Fondamentaux
Points forts : {', '.join(fundamental['strengths']) or 'A confirmer'}.
Points faibles : {', '.join(fundamental['weaknesses']) or 'Aucun point majeur dans les donnees disponibles'}.

## Dividende
Rendement : {dividend['dividend_yield']} %
Payout ratio : {dividend['payout_ratio']} %
Croissance 5 ans : {dividend['dividend_growth_5y']} %
Risque de reduction : {dividend['risk_of_dividend_cut']}.

## Analyse technique
Tendance : {technical['trend']}
Support : {levels['support']}
Resistance : {levels['resistance']}
RSI : {technical['rsi']}
Zone d'entree theorique : {levels['entry_zone_low']} - {levels['entry_zone_high']}

## Actualites
Sentiment : {news['sentiment']}
Evenements importants : {', '.join(news['major_events']) or 'Aucun evenement majeur positif'}.
Risques : {', '.join(news['risks']) or 'Aucun risque majeur detecte dans le flux mock'}.

## Scenarios probabilistes
Hausse 30 jours : {probabilities['up_30d']} %
Baisse sous support : {probabilities['down_to_support']} %
Atteinte objectif 1 : {probabilities['hit_target_1']} %
Atteinte stop : {probabilities['hit_stop']} %
Confiance du signal : {probabilities['confidence']}

## Plan theorique
Zone d'entree : {levels['entry_zone_low']} - {levels['entry_zone_high']}
Stop theorique : {levels['stop_loss']}
Objectif 1 : {levels['target_1']}
Objectif 2 : {levels['target_2']}

## Contre-arguments
{chr(10).join('- ' + warning for warning in analysis['behavioral_warning'])}

## Mention importante
{settings.compliance_notice}
"""
