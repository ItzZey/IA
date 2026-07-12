# Dividend AI Watcher

Assistant educatif de veille boursiere specialise dans les actions a dividendes.

L'application produit des analyses probabilistes, des scores et des scenarios prudents. Elle ne constitue pas un conseil financier personnalise.

## Lancement local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --app-dir app
streamlit run app/frontend/streamlit_app.py
```

## Deploiement Streamlit Cloud

Fichier principal a selectionner :

```text
app/frontend/streamlit_app.py
```

Les dependances sont declarees dans `requirements.txt` a la racine.

## Tests

```bash
pytest app/tests
```

## MVP inclus

- Backend FastAPI
- Frontend Streamlit
- Provider Yahoo Finance via `yfinance`
- Provider mock de secours si une source externe echoue
- Analyse technique
- Analyse fondamentale simplifiee
- Analyse dividende
- Valorisation
- Analyse news via Yahoo Finance quand disponible
- Scoring global
- Probabilites simples
- Gestion du risque
- Rapport explicatif
- Watchlist en memoire
- Backtest simple
- Tests unitaires

## Donnees reelles

La V1 interroge Yahoo Finance via `yfinance` pour :

- profil de l'entreprise
- historique OHLCV sur 1 an
- ratios financiers disponibles
- historique des dividendes
- actualites disponibles

Si une source echoue ou ne retourne pas de donnees, l'application utilise le provider mock uniquement pour garder l'interface fonctionnelle. Le bloc `Sources et diagnostics` indique quelles donnees sont reelles et quelles donnees proviennent du fallback.
