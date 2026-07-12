import sys
from pathlib import Path
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import settings  # noqa: E402
from backend.services.stock_service import (  # noqa: E402
    add_to_watchlist,
    analyze_stock,
    backtest_stock,
    get_price_history_records,
    get_watchlist,
    remove_from_watchlist,
)


st.set_page_config(page_title="Dividend AI Watcher", page_icon="D", layout="wide")

st.markdown(
    """
    <style>
    .metric-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.75rem 0.85rem;
        background: #ffffff;
        min-height: 92px;
    }
    .metric-label {
        color: #4b5563;
        font-size: 0.86rem;
        margin-bottom: 0.28rem;
        white-space: nowrap;
    }
    .metric-value {
        color: #111827;
        font-size: 1.55rem;
        font-weight: 650;
        line-height: 1.18;
        word-break: break-word;
    }
    .source-pill {
        display: inline-block;
        margin: 0.1rem 0.25rem 0.1rem 0;
        padding: 0.18rem 0.48rem;
        border-radius: 999px;
        background: #eef2ff;
        color: #3730a3;
        font-size: 0.82rem;
    }
    .watch-item {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.75rem 0.85rem;
        margin-bottom: 0.55rem;
        background: #ffffff;
    }
    .watch-title {
        font-weight: 650;
        color: #111827;
        margin-bottom: 0.25rem;
    }
    .watch-meta {
        color: #6b7280;
        font-size: 0.82rem;
        margin-bottom: 0.25rem;
    }
    .watch-badge {
        display: inline-block;
        padding: 0.12rem 0.42rem;
        border-radius: 999px;
        font-size: 0.78rem;
        margin-right: 0.25rem;
        background: #f3f4f6;
        color: #374151;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_card(column, label: str, value: str) -> None:
    column.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def source_label(method: str) -> str:
    return method.replace("get_", "").replace("_", " ")


def render_watch_item(item: dict) -> None:
    title = item.get("title", "Actualite sans titre")
    meta = f"{item.get('ticker', '')} - {item.get('scope', '')} - importance {item.get('importance', 0)}/100"
    source = item.get("source") or "source non renseignee"
    summary = item.get("summary") or ""
    badges = [item.get("classification_label", item.get("classification", "a surveiller"))]
    if item.get("dividend_relevance"):
        badges.append("dividende")
    if item.get("macro_relevance"):
        badges.append("macro")
    badge_html = " ".join(f'<span class="watch-badge">{escape(badge)}</span>' for badge in badges)
    summary_html = (
        f'<div style="margin-top:0.35rem;color:#374151;font-size:0.92rem;">{escape(summary)}</div>'
        if summary
        else ""
    )
    st.markdown(
        f"""
        <div class="watch-item">
            <div class="watch-title">{escape(title)}</div>
            <div class="watch-meta">{escape(meta)} - {escape(source)}</div>
            {badge_html}
            {summary_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


st.title("Dividend AI Watcher")
st.caption(settings.compliance_notice)

with st.sidebar:
    st.header("Watchlist")
    ticker = st.text_input("Ticker", value="TTE.PA").upper().strip()
    col_add, col_remove = st.columns(2)
    with col_add:
        if st.button("Ajouter", use_container_width=True):
            add_to_watchlist(ticker)
    with col_remove:
        if st.button("Retirer", use_container_width=True):
            remove_from_watchlist(ticker)
    selected = st.selectbox("Actions suivies", get_watchlist(), index=0)
    if st.button("Analyser la selection", use_container_width=True):
        ticker = selected
    if st.button("Rafraichir les donnees", use_container_width=True):
        st.rerun()


analysis = analyze_stock(ticker)
prices = pd.DataFrame(get_price_history_records(ticker))
prices["date"] = pd.to_datetime(prices["date"])

st.subheader(f"{analysis['name']} ({analysis['ticker']})")
sources = analysis.get("data_diagnostics", {}).get("sources", {})
if sources:
    source_html = " ".join(
        f'<span class="source-pill">{source_label(key)}: {value}</span>' for key, value in sources.items()
    )
else:
    source_html = '<span class="source-pill">source non chargee - rafraichir la page</span>'
st.markdown(f"Sources de donnees : {source_html}", unsafe_allow_html=True)

top_row_1 = st.columns(3)
render_card(top_row_1[0], "Prix", f"{analysis['price']} {analysis['currency']}")
render_card(top_row_1[1], "Score global", f"{analysis['scores']['global']}/100")
render_card(top_row_1[2], "Risque", analysis["risk_level"])

top_row_2 = st.columns(2)
render_card(top_row_2[0], "Probabilite de hausse a 30 jours", f"{analysis['probabilities']['up_30d']} %")
render_card(top_row_2[1], "Confiance du signal", analysis["probabilities"]["confidence"])

st.markdown("### Scores detailles")
score_row_1 = st.columns(3)
score_row_2 = st.columns(3)
score_items = [
    ("Fondamental", "fundamental"),
    ("Dividende", "dividend"),
    ("Valorisation", "valuation"),
    ("Technique", "technical"),
    ("Actualites", "news"),
    ("Risque", "risk"),
]
for col, (label, key) in zip(score_row_1 + score_row_2, score_items):
    render_card(col, label, f"{analysis['scores'][key]}/100")

fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=prices["date"],
    open=prices["open"],
    high=prices["high"],
    low=prices["low"],
    close=prices["close"],
    name="Prix",
))
fig.add_hline(y=analysis["levels"]["support"], line_dash="dot", annotation_text="Support")
fig.add_hline(y=analysis["levels"]["resistance"], line_dash="dot", annotation_text="Resistance")
fig.update_layout(height=460, xaxis_rangeslider_visible=False, margin=dict(l=20, r=20, t=20, b=20))
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns([1, 1])
with left:
    st.subheader("Plan theorique")
    st.write({
        "zone_entree": f"{analysis['levels']['entry_zone_low']} - {analysis['levels']['entry_zone_high']}",
        "stop": analysis["levels"]["stop_loss"],
        "objectif_1": analysis["levels"]["target_1"],
        "objectif_2": analysis["levels"]["target_2"],
        "decision": analysis["decision"],
    })

    st.subheader("Probabilites")
    st.write(analysis["probabilities"])

with right:
    st.subheader("Alertes et risques")
    if analysis["alerts"]:
        for alert in analysis["alerts"]:
            st.warning(f"{alert['type']} - {alert['message']}")
    else:
        st.success("Aucune alerte majeure dans les donnees disponibles")

    st.subheader("Contre-arguments")
    for warning in analysis["behavioral_warning"]:
        st.write(f"- {warning}")

tabs = st.tabs(["Rapport IA", "Veille strategique", "Details", "Backtest"])
with tabs[0]:
    st.markdown(analysis["report"])
with tabs[1]:
    watch = analysis["details"]["strategic_watch"]
    st.subheader("Veille strategique")
    st.caption("Surveille les actualites entreprise, concurrents, secteur et macro selon le profil de l'action.")

    watch_cols = st.columns(4)
    render_card(watch_cols[0], "Urgence", watch["urgency"])
    render_card(watch_cols[1], "Sentiment de veille", watch["sentiment"])
    render_card(watch_cols[2], "Pression risque", str(watch["risk_pressure"]))
    render_card(watch_cols[3], "Impact dividende", watch["dividend_impact"])

    st.markdown("#### Sources surveillees")
    source_badges = " ".join(
        f'<span class="source-pill">{ticker}: {scope}</span>' for ticker, scope in watch["watched_sources"].items()
    )
    st.markdown(source_badges, unsafe_allow_html=True)

    st.markdown("#### Themes suivis")
    theme_badges = " ".join(f'<span class="source-pill">{theme}</span>' for theme in watch["themes"])
    st.markdown(theme_badges, unsafe_allow_html=True)

    col_risk, col_opp = st.columns(2)
    with col_risk:
        st.markdown("#### Risques detectes")
        if watch["risks"]:
            for item in watch["risks"]:
                render_watch_item(item)
        else:
            st.success("Aucun risque majeur detecte dans la veille actuelle.")
    with col_opp:
        st.markdown("#### Opportunites detectees")
        if watch["opportunities"]:
            for item in watch["opportunities"]:
                render_watch_item(item)
        else:
            st.info("Aucune opportunite majeure detectee dans la veille actuelle.")

    st.markdown("#### Macro / secteur a surveiller")
    if watch["macro_alerts"]:
        for item in watch["macro_alerts"]:
            render_watch_item(item)
    else:
        st.info("Aucun signal macro/secteur significatif dans la veille actuelle.")

    with st.expander("Evenements neutres ou a suivre"):
        for item in watch["watch_items"]:
            render_watch_item(item)

    if watch["errors"]:
        with st.expander("Erreurs de collecte de veille"):
            st.json(watch["errors"])

with tabs[2]:
    st.subheader("Sources et diagnostics")
    st.json(analysis.get("data_diagnostics", {}))
    st.subheader("Details d'analyse")
    st.json(analysis["details"])
with tabs[3]:
    st.write(backtest_stock(ticker))
