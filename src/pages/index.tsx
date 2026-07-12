"use client";

import { AlertTriangle, ArrowDownRight, ArrowUpRight, BarChart3, BellRing, CalendarClock, CheckCircle2, CircleDollarSign, Newspaper, RefreshCw, Search, ShieldCheck, Sparkles, Target, TrendingUp } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";
import type { AnalysisResult, NewsItem, PricePoint } from "@/lib/finance";

const QUICK_TICKERS = ["TTE.PA", "KO", "PEP", "JNJ", "SAN.PA", "MSFT", "AIR.PA"];

function formatNumber(value: number, suffix = "") {
  return `${new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2 }).format(value)}${suffix}`;
}

function formatDate(value: string) {
  if (!value) return "date non renseignee";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("fr-FR", { dateStyle: "medium" }).format(date);
}

function Metric({ label, value, helper, tone = "neutral" }: { label: string; value: string; helper?: string; tone?: "neutral" | "good" | "warning" | "danger" }) {
  return (
    <div className={`metric metric-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {helper ? <small>{helper}</small> : null}
    </div>
  );
}

function scoreTone(value: number) {
  if (value >= 70) return "good";
  if (value >= 50) return "warning";
  return "danger";
}

function scoreLabel(value: number) {
  if (value >= 80) return "Tres bon";
  if (value >= 70) return "Bon";
  if (value >= 50) return "Moyen";
  return "A surveiller";
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  const tone = scoreTone(value);

  return (
    <div className={`score-row score-${tone}`}>
      <div className="score-row-header">
        <span>{label}</span>
        <div>
          <em>{scoreLabel(value)}</em>
          <strong>{formatNumber(value)}/100</strong>
        </div>
      </div>
      <div className="score-track" aria-hidden="true">
        <i style={{ width: `${Math.max(3, Math.min(100, value))}%` }} />
      </div>
    </div>
  );
}

function PriceChart({ history }: { history: PricePoint[] }) {
  const path = useMemo(() => {
    const points = history.slice(-180);
    if (points.length < 2) return "";
    const width = 760;
    const height = 260;
    const closes = points.map((point) => point.close);
    const min = Math.min(...closes);
    const max = Math.max(...closes);
    const range = max - min || 1;
    return points
      .map((point, index) => {
        const x = (index / (points.length - 1)) * width;
        const y = height - ((point.close - min) / range) * height;
        return `${x.toFixed(2)},${y.toFixed(2)}`;
      })
      .join(" ");
  }, [history]);

  return (
    <div className="chart-shell">
      <svg viewBox="0 0 760 260" role="img" aria-label="Evolution du prix sur les derniers mois">
        <defs>
          <linearGradient id="lineGradient" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" stopColor="#0f766e" />
            <stop offset="100%" stopColor="#2563eb" />
          </linearGradient>
        </defs>
        <line x1="0" y1="214" x2="760" y2="214" />
        <line x1="0" y1="130" x2="760" y2="130" />
        <line x1="0" y1="46" x2="760" y2="46" />
        {path ? <polyline points={path} /> : null}
      </svg>
    </div>
  );
}

function NewsCard({ item }: { item: NewsItem }) {
  return (
    <a className="news-card" href={item.link} target="_blank" rel="noreferrer">
      <div className="news-topline">
        <span className={`impact impact-${item.impact}`}>{item.impact === "risque" ? "Risque" : item.impact === "opportunite" ? "Opportunite" : "Neutre"}</span>
        <span>{formatNumber(item.importance)}/100</span>
      </div>
      <strong>{item.title}</strong>
      <p>{item.summary}</p>
      <div className="tag-row">
        {item.tags.map((tag) => (
          <span key={tag}>{tag}</span>
        ))}
      </div>
      <small>{item.source} - {formatDate(item.publishedAt)}</small>
    </a>
  );
}

export default function Page() {
  const [ticker, setTicker] = useState("TTE.PA");
  const [data, setData] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runAnalysis(nextTicker = ticker) {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`/api/analyze?ticker=${encodeURIComponent(nextTicker)}`);
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "Analyse impossible");
      setData(payload);
      setTicker(payload.ticker);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    runAnalysis();
  }

  const trendTone = data?.dayChangePercent && data.dayChangePercent >= 0 ? "good" : "danger";
  const allNews = [...(data?.watch.risks || []), ...(data?.watch.opportunities || [])];

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark">
          <CircleDollarSign />
          <div>
            <strong>Dividend AI</strong>
            <span>Watcher</span>
          </div>
        </div>
        <nav>
          <a href="#analyse"><BarChart3 /> Analyse</a>
          <a href="#veille"><BellRing /> Veille</a>
          <a href="#methode"><ShieldCheck /> Methode</a>
        </nav>
        <div className="side-note">
          <Sparkles />
          <p>Donnees publiques actualisees cote serveur. Les scores aident a comparer, ils ne remplacent pas une decision d'investissement.</p>
        </div>
      </aside>

      <section className="content">
        <header className="hero" id="analyse">
          <div>
            <p className="eyebrow">Tableau de bord dividendes</p>
            <h1>Comprendre rapidement une action a dividende.</h1>
            <p>Prix, tendance, qualite du dividende, valorisation, risques et veille d'actualites sont regroupes dans une interface lisible.</p>
          </div>
          <form className="search-panel" onSubmit={onSubmit}>
            <label htmlFor="ticker">Symbole boursier</label>
            <div>
              <Search />
              <input id="ticker" value={ticker} onChange={(event) => setTicker(event.target.value.toUpperCase())} placeholder="Ex : TTE.PA, KO, MSFT" />
              <button type="submit" disabled={loading}>{loading ? <RefreshCw className="spin" /> : <TrendingUp />}Analyser</button>
            </div>
            <div className="quick-row">
              {QUICK_TICKERS.map((quickTicker) => (
                <button type="button" key={quickTicker} onClick={() => runAnalysis(quickTicker)}>{quickTicker}</button>
              ))}
            </div>
          </form>
        </header>

        {error ? <div className="error-box"><AlertTriangle /> {error}</div> : null}

        {!data ? (
          <section className="empty-state">
            <Target />
            <h2>Lance une analyse pour voir le diagnostic complet.</h2>
            <p>Exemple conseille : TotalEnergies avec le symbole TTE.PA.</p>
            <button type="button" onClick={() => runAnalysis("TTE.PA")} disabled={loading}>Analyser TotalEnergies</button>
          </section>
        ) : (
          <>
            <section className="summary-grid">
              <div className="company-panel">
                <div className="company-heading">
                  <div>
                    <span>{data.ticker}</span>
                    <h2>{data.name}</h2>
                    <p>{data.sector} - source : {data.source}</p>
                  </div>
                  <div className={`score-badge score-${scoreTone(data.scoreGlobal)}`}>
                    <strong>{formatNumber(data.scoreGlobal)}</strong>
                    <span>/100</span>
                    <small>{scoreLabel(data.scoreGlobal)}</small>
                  </div>
                </div>
                <PriceChart history={data.history} />
              </div>

              <div className="decision-panel">
                <Metric label="Prix actuel" value={`${formatNumber(data.price)} ${data.currency}`} helper={`Maj ${formatDate(data.updatedAt)}`} />
                <Metric label="Variation jour" value={formatNumber(data.dayChangePercent, " %")} helper={`Cloture precedente : ${formatNumber(data.previousClose)}`} tone={trendTone} />
                <Metric label="Risque" value={data.riskLevel} helper={`Confiance ${data.confidence}`} tone={data.riskLevel === "Faible" ? "good" : data.riskLevel === "Modere" ? "warning" : "danger"} />
                <Metric label="Potentiel 1 an" value={formatNumber(data.yearUpsidePercent, " %")} helper="Vers le plus haut annuel" tone={data.yearUpsidePercent > 10 ? "good" : "neutral"} />
              </div>
            </section>

            <section className="detail-grid">
              <div className="panel">
                <div className="panel-title"><CheckCircle2 /> Scores detailles</div>
                <ScoreBar label="Fondamental" value={data.scores.fondamental} />
                <ScoreBar label="Dividende" value={data.scores.dividende} />
                <ScoreBar label="Valorisation" value={data.scores.valorisation} />
                <ScoreBar label="Technique" value={data.scores.technique} />
                <ScoreBar label="Actualites" value={data.scores.actualites} />
                <ScoreBar label="Risque" value={data.scores.risque} />
              </div>

              <div className="panel">
                <div className="panel-title"><CalendarClock /> Points a surveiller</div>
                <div className="mini-grid">
                  <Metric label="Rendement" value={formatNumber(data.dividend.yieldPercent, " %")} helper={`Dividende annuel : ${formatNumber(data.dividend.annualDividend)}`} />
                  <Metric label="Payout ratio" value={formatNumber(data.dividend.payoutRatio, " %")} helper="Part du profit distribuee" />
                  <Metric label="PER" value={formatNumber(data.valuation.pe)} helper={`Forward PER : ${formatNumber(data.valuation.forwardPe)}`} />
                  <Metric label="Tendance" value={data.technical.trend} helper={`Volatilite : ${formatNumber(data.technical.volatility, " %")}`} />
                </div>
              </div>
            </section>

            <section className="watch-section" id="veille">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">Veille strategique</p>
                  <h2>Actualites classees par enjeu</h2>
                </div>
                <div className="theme-row">
                  {data.watch.themes.map((theme) => <span key={theme}>{theme}</span>)}
                </div>
              </div>

              <div className="news-grid">
                <div>
                  <h3><ArrowDownRight /> Risques detectes</h3>
                  {data.watch.risks.length ? data.watch.risks.map((item) => <NewsCard key={item.link} item={item} />) : <p className="soft-text">Aucun risque fort detecte dans les dernieres actualites recuperees.</p>}
                </div>
                <div>
                  <h3><ArrowUpRight /> Opportunites detectees</h3>
                  {data.watch.opportunities.length ? data.watch.opportunities.map((item) => <NewsCard key={item.link} item={item} />) : <p className="soft-text">Aucune opportunite forte detectee pour le moment.</p>}
                </div>
              </div>
            </section>

            <section className="method-section" id="methode">
              <div>
                <p className="eyebrow">Lecture simple</p>
                <h2>Comment interpreter le resultat</h2>
              </div>
              <div className="method-grid">
                <div><strong>Score global</strong><p>Moyenne des signaux fondamentaux, dividende, valorisation, technique, actualites et risque.</p></div>
                <div><strong>Risque</strong><p>Combine volatilite, tendance, payout ratio et signaux negatifs issus de la veille.</p></div>
                <div><strong>Veille</strong><p>Les articles publics sont classes en risques ou opportunites selon les mots-clefs et les themes du secteur.</p></div>
              </div>
            </section>
          </>
        )}
      </section>
    </main>
  );
}
