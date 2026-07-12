export type PricePoint = {
  date: string;
  close: number;
};

type DividendEvent = {
  date: string;
  amount: number;
};

export type NewsItem = {
  title: string;
  link: string;
  source: string;
  publishedAt: string;
  summary: string;
  tags: string[];
  impact: "risque" | "opportunite" | "neutre";
  importance: number;
};

export type AnalysisResult = {
  ticker: string;
  name: string;
  currency: string;
  sector: string;
  source: string;
  price: number;
  previousClose: number;
  dayChangePercent: number;
  yearUpsidePercent: number;
  scoreGlobal: number;
  confidence: "haute" | "moyenne" | "faible";
  riskLevel: "Faible" | "Modere" | "Eleve";
  scores: {
    fondamental: number;
    dividende: number;
    valorisation: number;
    technique: number;
    actualites: number;
    risque: number;
  };
  dividend: {
    yieldPercent: number;
    annualDividend: number;
    payoutRatio: number;
    exDate: string | null;
  };
  valuation: {
    pe: number;
    forwardPe: number;
    targetMeanPrice: number;
  };
  technical: {
    trend: "haussiere" | "neutre" | "baissiere";
    sma50: number;
    sma200: number;
    volatility: number;
  };
  watch: {
    themes: string[];
    risks: NewsItem[];
    opportunities: NewsItem[];
  };
  history: PricePoint[];
  updatedAt: string;
};

type YahooQuote = {
  symbol?: string;
  longName?: string;
  shortName?: string;
  currency?: string;
  regularMarketPrice?: number;
  regularMarketPreviousClose?: number;
  regularMarketChangePercent?: number;
  chartPreviousClose?: number;
  fiftyTwoWeekHigh?: number;
  fiftyTwoWeekLow?: number;
  dividendYield?: number;
  dividendRate?: number;
  payoutRatio?: number;
  trailingPE?: number;
  forwardPE?: number;
  targetMeanPrice?: number;
  sector?: string;
  fiftyDayAverage?: number;
  twoHundredDayAverage?: number;
  exDividendDate?: number;
};

const DEFAULT_TICKERS = ["TTE.PA", "KO", "PEP", "JNJ", "SAN.PA", "MSFT", "AIR.PA"];

const KNOWN_SECTORS: Record<string, string> = {
  "TTE.PA": "Energy",
  KO: "Consumer Defensive",
  PEP: "Consumer Defensive",
  JNJ: "Healthcare",
  "SAN.PA": "Healthcare",
  MSFT: "Technology",
  "AIR.PA": "Industrials"
};

const SECTOR_THEMES: Record<string, { themes: string[]; competitors: string[] }> = {
  energy: { themes: ["petrole", "gaz", "marges", "transition energetique", "geopolitique"], competitors: ["SHEL", "XOM", "CVX"] },
  "consumer defensive": { themes: ["inflation", "marges", "volumes", "pricing power", "devises"], competitors: ["PEP", "MDLZ", "MNST"] },
  healthcare: { themes: ["brevets", "pipeline", "reglementation", "marges", "rachat actions"], competitors: ["PFE", "MRK", "NVS"] },
  technology: { themes: ["cloud", "ia", "marges", "cybersecurite", "capex"], competitors: ["AAPL", "GOOGL", "ORCL"] },
  industrials: { themes: ["commandes", "supply chain", "defense", "aviation", "marges"], competitors: ["GE", "HON", "BA"] }
};

function clamp(value: number, min = 0, max = 100) {
  return Math.max(min, Math.min(max, value));
}

function round(value: number, digits = 1) {
  if (!Number.isFinite(value)) return 0;
  const power = 10 ** digits;
  return Math.round(value * power) / power;
}

function average(values: number[]) {
  const clean = values.filter(Number.isFinite);
  if (!clean.length) return 0;
  return clean.reduce((sum, value) => sum + value, 0) / clean.length;
}

function normalizeTicker(input: string) {
  return (input || "TTE.PA").trim().toUpperCase();
}

function sectorSettings(sector: string) {
  const normalized = sector.toLowerCase();
  const match = Object.keys(SECTOR_THEMES).find((key) => normalized.includes(key));
  return match ? SECTOR_THEMES[match] : { themes: ["dividende", "resultats", "marges", "dette", "guidance"], competitors: DEFAULT_TICKERS };
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 DividendAIWatcher/1.0",
      Accept: "application/json,text/plain,*/*"
    },
    next: { revalidate: 300 }
  });

  if (!response.ok) {
    throw new Error(`Source indisponible (${response.status})`);
  }

  return response.json() as Promise<T>;
}

async function fetchText(url: string): Promise<string> {
  const response = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 DividendAIWatcher/1.0",
      Accept: "application/rss+xml,text/xml,text/plain,*/*"
    },
    next: { revalidate: 600 }
  });

  if (!response.ok) {
    return "";
  }

  return response.text();
}

async function getQuote(ticker: string) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?range=1y&interval=1d&events=div%2Csplits`;
  const data = await fetchJson<{ chart?: { result?: Array<{ meta?: YahooQuote }> } }>(url);
  const quote = data.chart?.result?.[0]?.meta;
  if (!quote || !quote.regularMarketPrice) {
    throw new Error("Aucune cotation trouvee pour ce symbole.");
  }
  return quote;
}

async function getHistory(ticker: string): Promise<PricePoint[]> {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?range=1y&interval=1d&events=div%2Csplits`;
  const data = await fetchJson<{
    chart?: {
      result?: Array<{
        timestamp?: number[];
        indicators?: { quote?: Array<{ close?: Array<number | null> }> };
      }>;
    };
  }>(url);
  const result = data.chart?.result?.[0];
  const timestamps = result?.timestamp || [];
  const closes = result?.indicators?.quote?.[0]?.close || [];

  return timestamps
    .map((timestamp, index) => {
      const close = closes[index];
      if (!close) return null;
      return { date: new Date(timestamp * 1000).toISOString().slice(0, 10), close: round(close, 2) };
    })
    .filter((point): point is PricePoint => Boolean(point));
}

async function getDividendEvents(ticker: string): Promise<DividendEvent[]> {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?range=1y&interval=1d&events=div`;
  const data = await fetchJson<{
    chart?: {
      result?: Array<{
        events?: {
          dividends?: Record<string, { amount?: number; date?: number }>;
        };
      }>;
    };
  }>(url);

  const dividends = data.chart?.result?.[0]?.events?.dividends || {};
  return Object.values(dividends)
    .map((event) => {
      if (!event.amount || !event.date) return null;
      return {
        amount: event.amount,
        date: new Date(event.date * 1000).toISOString().slice(0, 10)
      };
    })
    .filter((event): event is DividendEvent => Boolean(event));
}


function decodeHtml(text: string) {
  return text
    .replace(/<!\[CDATA\[(.*?)\]\]>/gs, "$1")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">");
}

function stripHtml(text: string) {
  return decodeHtml(text).replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}

function translateTitle(title: string) {
  const replacements: Array<[RegExp, string]> = [
    [/Could Be ([\d.,]+)% Undervalued On Its LNG Growth Narrative/gi, "pourrait etre sous-valorisee de $1 % selon son scenario de croissance GNL"],
    [/Ships First Mexico LNG Cargo And Exits European Rooftop Solar/gi, "expedie son premier cargo GNL depuis le Mexique et sort du solaire distribue en Europe"],
    [/LNG/gi, "GNL"],
    [/liquefied natural gas/gi, "gaz naturel liquefie"],
    [/undervalued/gi, "sous-valorisee"],
    [/growth narrative/gi, "scenario de croissance"],
    [/ships first/gi, "expedie son premier"],
    [/cargo/gi, "cargo"],
    [/exits/gi, "sort de"],
    [/rooftop solar/gi, "solaire en toiture"],
    [/dividend stocks?/gi, "actions a dividendes"],
    [/dividend/gi, "dividende"],
    [/stocks?/gi, "actions"],
    [/buy/gi, "acheter"],
    [/investors?/gi, "investisseurs"],
    [/earnings/gi, "resultats"],
    [/growth/gi, "croissance"],
    [/risk/gi, "risque"],
    [/why/gi, "Pourquoi"],
    [/today/gi, "aujourd'hui"],
    [/outlook/gi, "perspectives"]
  ];

  return replacements.reduce((value, [pattern, replacement]) => value.replace(pattern, replacement), title);
}

function translateFinancialText(text: string) {
  const replacements: Array<[RegExp, string]> = [
    [/has shipped its first/gi, "a expedie son premier"],
    [/newly commissioned/gi, "nouvellement mis en service"],
    [/liquefied natural gas/gi, "gaz naturel liquefie"],
    [/LNG/gi, "GNL"],
    [/from the ECA GNL Phase 1 terminal in Mexico to Asia/gi, "depuis le terminal ECA GNL Phase 1 au Mexique vers l'Asie"],
    [/from the ECA LNG Phase 1 terminal in Mexico to Asia/gi, "depuis le terminal ECA LNG Phase 1 au Mexique vers l'Asie"],
    [/highlighting/gi, "ce qui met en avant"],
    [/long-term offtake role/gi, "un role d'acheteur a long terme"],
    [/exposure to Pacific Basin gas flows/gi, "une exposition aux flux gaziers du bassin Pacifique"],
    [/See our latest analysis for/gi, "Voir la derniere analyse sur"],
    [/The LNG milestone comes after/gi, "Cette etape dans le GNL intervient apres"],
    [/a mixed period for the stock/gi, "une periode contrastee pour l'action"],
    [/share price/gi, "cours de l'action"],
    [/total shareholder return/gi, "rendement total pour l'actionnaire"],
    [/The company has exited distributed solar generation/gi, "L'entreprise est sortie de la production solaire distribuee"],
    [/selling its rooftop solar portfolio/gi, "en vendant son portefeuille solaire en toiture"],
    [/The moves highlight a shift toward/gi, "Ces mouvements montrent un recentrage vers"],
    [/North American/gi, "nord-americain"],
    [/renewable projects/gi, "projets renouvelables"],
    [/global multi-energy company/gi, "groupe mondial multi-energies"],
    [/oil, gas and renewables/gi, "petrole, gaz et renouvelables"],
    [/undervalued/gi, "sous-valorisee"],
    [/growth/gi, "croissance"],
    [/risk/gi, "risque"],
    [/opportunity/gi, "opportunite"]
  ];

  return replacements.reduce((value, [pattern, replacement]) => value.replace(pattern, replacement), text);
}

function classifyNews(title: string, summary: string, themes: string[]): Pick<NewsItem, "impact" | "importance" | "tags"> {
  const text = `${title} ${summary}`.toLowerCase();
  const riskWords = ["cut", "debt", "lawsuit", "probe", "warning", "fall", "drop", "downgrade", "risk", "weak", "proces", "vigilance", "baisse", "dette", "critique", "faiblesse"];
  const opportunityWords = ["buy", "upgrade", "growth", "raise", "record", "strong", "beat", "expansion", "opportunity", "croissance", "progresse", "hausse", "cession", "expedie", "renouvelables"];
  const matchedThemes = themes.filter((theme) => text.includes(theme.toLowerCase().split(" ")[0]));
  const riskHits = riskWords.filter((word) => text.includes(word)).length;
  const opportunityHits = opportunityWords.filter((word) => text.includes(word)).length;
  const importance = clamp(45 + matchedThemes.length * 12 + Math.max(riskHits, opportunityHits) * 10, 25, 100);

  if (riskHits > opportunityHits) return { impact: "risque", importance, tags: ["risque", ...matchedThemes].slice(0, 4) };
  if (opportunityHits > riskHits) return { impact: "opportunite", importance, tags: ["opportunite", ...matchedThemes].slice(0, 4) };
  return { impact: "neutre", importance, tags: matchedThemes.length ? matchedThemes.slice(0, 3) : ["actualite"] };
}

async function getNews(ticker: string, themes: string[]): Promise<NewsItem[]> {
  const rss = await fetchText(`https://feeds.finance.yahoo.com/rss/2.0/headline?s=${encodeURIComponent(ticker)}&region=FR&lang=fr-FR`);
  if (!rss) return [];

  const items = [...rss.matchAll(/<item>([\s\S]*?)<\/item>/g)].slice(0, 12);
  return items.map((match) => {
    const item = match[1];
    const rawTitle = stripHtml(item.match(/<title>([\s\S]*?)<\/title>/)?.[1] || "Actualite financiere");
    const title = translateTitle(rawTitle);
    const link = stripHtml(item.match(/<link>([\s\S]*?)<\/link>/)?.[1] || "#");
    const publishedAt = stripHtml(item.match(/<pubDate>([\s\S]*?)<\/pubDate>/)?.[1] || "");
    const summary = translateFinancialText(stripHtml(item.match(/<description>([\s\S]*?)<\/description>/)?.[1] || ""));
    const classified = classifyNews(rawTitle, summary, themes);
    return {
      title,
      link,
      source: "Yahoo Finance",
      publishedAt,
      summary: summary || "Article detecte dans la veille financiere.",
      ...classified
    };
  });
}

function computeVolatility(history: PricePoint[]) {
  const returns = history.slice(1).map((point, index) => {
    const previous = history[index].close;
    return previous ? (point.close - previous) / previous : 0;
  });
  const mean = average(returns);
  const variance = average(returns.map((value) => (value - mean) ** 2));
  return Math.sqrt(variance) * Math.sqrt(252) * 100;
}

function sma(history: PricePoint[], days: number) {
  return average(history.slice(-days).map((point) => point.close));
}

export async function analyzeTicker(rawTicker: string): Promise<AnalysisResult> {
  const ticker = normalizeTicker(rawTicker);
  const [quote, history, dividends] = await Promise.all([getQuote(ticker), getHistory(ticker), getDividendEvents(ticker)]);
  const sector = quote.sector || KNOWN_SECTORS[ticker] || "Non renseigne";
  const settings = sectorSettings(sector);
  const news = await getNews(ticker, settings.themes);

  const price = quote.regularMarketPrice || history.at(-1)?.close || 0;
  const previousClose = quote.regularMarketPreviousClose || history.at(-2)?.close || quote.chartPreviousClose || price;
  const dayChangePercent = quote.regularMarketChangePercent ?? ((price - previousClose) / previousClose) * 100;
  const oneYearLow = quote.fiftyTwoWeekLow || Math.min(...history.map((point) => point.close));
  const oneYearHigh = quote.fiftyTwoWeekHigh || Math.max(...history.map((point) => point.close));
  const yearUpsidePercent = oneYearHigh ? ((oneYearHigh - price) / price) * 100 : 0;
  const sma50 = quote.fiftyDayAverage || sma(history, 50);
  const sma200 = quote.twoHundredDayAverage || sma(history, 200);
  const volatility = computeVolatility(history);
  const annualDividend = dividends.reduce((sum, event) => sum + event.amount, 0) || quote.dividendRate || 0;
  const dividendYield = quote.dividendYield
    ? quote.dividendYield * (quote.dividendYield < 1 ? 100 : 1)
    : price
      ? (annualDividend / price) * 100
      : 0;
  const payoutRatio = (quote.payoutRatio || 0) * (quote.payoutRatio && quote.payoutRatio < 1 ? 100 : 1);
  const pe = quote.trailingPE || 0;
  const targetMeanPrice = quote.targetMeanPrice || oneYearHigh;

  const fondamental = clamp(72 - Math.max(pe - 18, 0) * 1.1 + (quote.forwardPE && quote.forwardPE < pe ? 8 : 0));
  const dividende = clamp(50 + dividendYield * 10 - Math.max(payoutRatio - 70, 0) * 0.6);
  const valorisation = clamp(58 + (targetMeanPrice ? ((targetMeanPrice - price) / price) * 85 : 0) - Math.max(pe - 22, 0));
  const technique = clamp(45 + (price > sma50 ? 16 : -10) + (sma50 > sma200 ? 14 : -8) - volatility * 0.35);
  const risk = clamp(92 - volatility * 0.9 - Math.max(payoutRatio - 80, 0) * 0.7);
  const actualites = clamp(55 + news.filter((item) => item.impact === "opportunite").length * 8 - news.filter((item) => item.impact === "risque").length * 7);
  const scoreGlobal = round(average([fondamental, dividende, valorisation, technique, actualites, risk]));

  return {
    ticker,
    name: quote.longName || quote.shortName || ticker,
    currency: quote.currency || "EUR",
    sector,
    source: "Yahoo Finance",
    price: round(price, 2),
    previousClose: round(previousClose, 2),
    dayChangePercent: round(dayChangePercent, 2),
    yearUpsidePercent: round(yearUpsidePercent, 1),
    scoreGlobal,
    confidence: history.length > 180 && news.length > 2 ? "haute" : history.length > 60 ? "moyenne" : "faible",
    riskLevel: risk >= 70 ? "Faible" : risk >= 45 ? "Modere" : "Eleve",
    scores: {
      fondamental: round(fondamental),
      dividende: round(dividende),
      valorisation: round(valorisation),
      technique: round(technique),
      actualites: round(actualites),
      risque: round(risk)
    },
    dividend: {
      yieldPercent: round(dividendYield, 2),
      annualDividend: round(annualDividend, 2),
      payoutRatio: round(payoutRatio, 1),
      exDate: quote.exDividendDate ? new Date(quote.exDividendDate * 1000).toISOString().slice(0, 10) : dividends.at(-1)?.date || null
    },
    valuation: {
      pe: round(pe, 1),
      forwardPe: round(quote.forwardPE || 0, 1),
      targetMeanPrice: round(targetMeanPrice, 2)
    },
    technical: {
      trend: price > sma50 && sma50 > sma200 ? "haussiere" : price < sma50 ? "baissiere" : "neutre",
      sma50: round(sma50, 2),
      sma200: round(sma200, 2),
      volatility: round(volatility, 1)
    },
    watch: {
      themes: settings.themes,
      risks: news.filter((item) => item.impact === "risque").slice(0, 4),
      opportunities: news.filter((item) => item.impact === "opportunite").slice(0, 4)
    },
    history,
    updatedAt: new Date().toISOString()
  };
}
