from fastapi import FastAPI

from backend.config import settings
from backend.database import init_db
from backend.services.stock_service import (
    add_to_watchlist,
    analyze_stock,
    backtest_stock,
    get_price_history_records,
    get_watchlist,
    remove_from_watchlist,
)

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {"app": settings.app_name, "notice": settings.compliance_notice}


@app.get("/stocks")
def stocks() -> dict[str, list[str]]:
    return {"stocks": get_watchlist()}


@app.get("/stocks/{ticker}")
def stock(ticker: str) -> dict:
    return analyze_stock(ticker)


@app.get("/prices/{ticker}")
def prices(ticker: str) -> dict:
    return {"ticker": ticker.upper(), "prices": get_price_history_records(ticker)}


@app.get("/analysis/{ticker}")
def analysis(ticker: str) -> dict:
    return analyze_stock(ticker)


@app.get("/analysis/{ticker}/fundamental")
def fundamental(ticker: str) -> dict:
    return analyze_stock(ticker)["details"]["fundamental"]


@app.get("/analysis/{ticker}/dividend")
def dividend(ticker: str) -> dict:
    return analyze_stock(ticker)["details"]["dividend"]


@app.get("/analysis/{ticker}/technical")
def technical(ticker: str) -> dict:
    return analyze_stock(ticker)["details"]["technical"]


@app.get("/analysis/{ticker}/news")
def news(ticker: str) -> dict:
    return analyze_stock(ticker)["details"]["news"]


@app.get("/analysis/{ticker}/strategic-watch")
def strategic_watch(ticker: str) -> dict:
    return analyze_stock(ticker)["details"]["strategic_watch"]


@app.get("/analysis/{ticker}/probability")
def probability(ticker: str) -> dict:
    return analyze_stock(ticker)["probabilities"]


@app.get("/watchlist")
def watchlist() -> dict[str, list[str]]:
    return {"watchlist": get_watchlist()}


@app.post("/watchlist/{ticker}")
def add_watchlist(ticker: str) -> dict[str, list[str]]:
    return {"watchlist": add_to_watchlist(ticker)}


@app.delete("/watchlist/{ticker}")
def delete_watchlist(ticker: str) -> dict[str, list[str]]:
    return {"watchlist": remove_from_watchlist(ticker)}


@app.get("/alerts/{ticker}")
def alerts(ticker: str) -> dict:
    return {"ticker": ticker.upper(), "alerts": analyze_stock(ticker)["alerts"]}


@app.post("/backtest/{ticker}")
def backtest(ticker: str) -> dict:
    return {"ticker": ticker.upper(), "backtest": backtest_stock(ticker)}
