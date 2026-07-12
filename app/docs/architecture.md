# Architecture

```text
app/
  backend/
    main.py
    config.py
    database.py
    models/
    providers/
    services/
  frontend/
    streamlit_app.py
  docs/
  tests/
```

La couche `providers` isole les sources de donnees. La V1 utilise `YFinanceMarketDataProvider` via `FallbackMarketDataProvider`, avec `MockMarketDataProvider` comme secours si Yahoo Finance ne repond pas ou si une donnee manque.

Les services d'analyse ne dependent pas d'une source precise, ce qui permettra d'ajouter ensuite d'autres fournisseurs : Alpha Vantage, Financial Modeling Prep, EODHD, Polygon, broker, ou API interne.
