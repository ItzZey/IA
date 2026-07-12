# Cahier des charges - Dividend AI Watcher

## Objectif

Creer une application de veille boursiere educative specialisee dans les actions a dividendes. Le systeme analyse les fondamentaux, les dividendes, la valorisation, les graphiques, les actualites, les risques et produit des scenarios probabilistes.

## Philosophie

1. Fondamental d'abord
2. Qualite du dividende ensuite
3. Valorisation
4. Timing technique
5. Actualites en confirmation
6. Risque toujours
7. Probabilites, jamais certitudes

## MVP

- Backend FastAPI
- Frontend Streamlit
- Base SQLite
- Provider Yahoo Finance via `yfinance`
- Fallback mock si une source reelle echoue
- Analyse technique
- Analyse fondamentale simplifiee
- Analyse dividende
- Valorisation
- News Yahoo Finance quand disponibles
- Scoring global
- Probabilites simples
- Risque et garde-fous comportementaux
- Watchlist
- Backtest simple
- Tests unitaires

## Regles de conformite

L'application ne doit jamais promettre de performance. Elle doit afficher que les analyses sont educatives et probabilistes, et que l'utilisateur reste responsable de ses decisions.
