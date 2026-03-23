import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const defaultPayload = {
  market: null,
  markets: [],
  source: "empty",
  message: "Loading...",
  summary: null,
  rows: [],
};

function formatNumber(value, maximumFractionDigits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "-";
  }
  return new Intl.NumberFormat("en-US", { maximumFractionDigits }).format(Number(value));
}

function formatCompact(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "-";
  }
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(Number(value));
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "-";
  }
  const number = Number(value);
  return `${number > 0 ? "+" : ""}${number.toFixed(2)}%`;
}

function getChangeTone(value) {
  if (value > 0) return "text-rose-400";
  if (value < 0) return "text-sky-400";
  return "text-slate-300";
}

function getCurrencySymbol(currencyCode) {
  if (currencyCode === "USD") return "$";
  if (currencyCode === "KRW") return "KRW ";
  return `${currencyCode ?? ""} `;
}

function getSymbolText(row) {
  return String(row?.symbol ?? "");
}

function ToolbarChip({ children }) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950/80 px-3 py-2 text-[11px] uppercase tracking-[0.18em] text-slate-400">
      {children}
    </div>
  );
}

function MetricTile({ label, value, tone = "text-slate-50" }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/70 px-4 py-3">
      <div className="text-[11px] uppercase tracking-[0.18em] text-slate-500">{label}</div>
      <div className={`mt-2 text-xl font-semibold ${tone}`}>{value}</div>
    </div>
  );
}

function App() {
  const [payload, setPayload] = useState(defaultPayload);
  const [selectedMarket, setSelectedMarket] = useState("us");
  const [filterText, setFilterText] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function requestSnapshot(market) {
    const response = await fetch(`${API_BASE}/api/snapshot?market=${market}`);
    if (!response.ok) {
      throw new Error(`Snapshot request failed with ${response.status}`);
    }
    return response.json();
  }

  async function fetchSnapshot(market) {
    setLoading(true);
    setError("");
    try {
      const data = await requestSnapshot(market);
      setPayload(data);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Snapshot load failed");
    } finally {
      setLoading(false);
    }
  }

  async function refreshSnapshot() {
    setRefreshing(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/api/refresh?market=${selectedMarket}`, { method: "POST" });
      if (!response.ok) {
        throw new Error(`Refresh request failed with ${response.status}`);
      }
      const data = await response.json();
      setPayload(data);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Refresh failed");
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    fetchSnapshot(selectedMarket);
  }, [selectedMarket]);

  const filteredRows = useMemo(() => {
    if (!filterText) return payload.rows;
    const keyword = filterText.toLowerCase();
    return payload.rows.filter(
      (row) =>
        getSymbolText(row).toLowerCase().includes(keyword) ||
        String(row.company_name ?? "").toLowerCase().includes(keyword),
    );
  }, [filterText, payload.rows]);

  const topGainers = useMemo(
    () => [...payload.rows].sort((a, b) => b.change_percent - a.change_percent).slice(0, 6),
    [payload.rows],
  );
  const topLosers = useMemo(
    () => [...payload.rows].sort((a, b) => a.change_percent - b.change_percent).slice(0, 6),
    [payload.rows],
  );

  const currencySymbol = getCurrencySymbol(payload.market?.currency_code);

  return (
    <main className="min-h-screen bg-[#0a0f19] text-slate-100">
      <div className="border-b border-slate-800 bg-[#111827]">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-500/15 text-sm font-bold text-sky-300">
              SV
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-50">Stock Vibe Screener</div>
              <div className="text-xs text-slate-400">TradingView-inspired market monitor</div>
            </div>
          </div>
          <div className="hidden items-center gap-2 lg:flex">
            <ToolbarChip>Quotes</ToolbarChip>
            <ToolbarChip>Overview</ToolbarChip>
            <ToolbarChip>Volume Leaders</ToolbarChip>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-[1600px] px-4 py-4 sm:px-6">
        <section className="rounded-2xl border border-slate-800 bg-[#111827] shadow-[0_20px_60px_rgba(0,0,0,0.28)]">
          <div className="border-b border-slate-800 px-4 py-4">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
              <div>
                <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Markets / Stocks / Most Active</div>
                <h1 className="mt-2 text-2xl font-semibold text-slate-50">
                  {payload.market?.region_label ?? "Most active stocks"}
                </h1>
                <p className="mt-1 text-sm text-slate-400">
                  Top 50 names ranked by daily volume with current price and day-over-day change.
                </p>
              </div>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                <div className="inline-flex rounded-xl border border-slate-800 bg-slate-950/70 p-1">
                  {[
                    { key: "us", label: "NASDAQ" },
                    { key: "kospi", label: "KOSPI" },
                  ].map((market) => (
                    <button
                      key={market.key}
                      type="button"
                      onClick={() => setSelectedMarket(market.key)}
                      className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                        selectedMarket === market.key
                          ? "bg-sky-500 text-slate-950"
                          : "text-slate-300 hover:bg-slate-800"
                      }`}
                    >
                      {market.label}
                    </button>
                  ))}
                </div>
                <button
                  type="button"
                  onClick={() => fetchSnapshot(selectedMarket)}
                  className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800"
                >
                  {loading ? "Loading..." : "Load cache"}
                </button>
                <button
                  type="button"
                  onClick={refreshSnapshot}
                  disabled={refreshing}
                  className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {refreshing ? "Refreshing..." : "Refresh"}
                </button>
              </div>
            </div>
          </div>

          <div className="border-b border-slate-800 px-4 py-3">
            <div className="flex flex-wrap items-center gap-2">
              {["Overview"].map((tab, index) => (
                <div
                  key={tab}
                  className={`rounded-md px-3 py-2 text-sm ${
                    index === 0
                      ? "bg-slate-50 text-slate-950"
                      : "border border-slate-800 bg-slate-950/70 text-slate-400"
                  }`}
                >
                  {tab}
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-3 border-b border-slate-800 px-4 py-4 md:grid-cols-2 xl:grid-cols-5">
            <MetricTile label="Data source" value={payload.source} tone="text-sky-300" />
            <MetricTile label="Rows" value={payload.summary?.rows ?? 0} />
            <MetricTile
              label="Gainers / Losers"
              value={`${payload.summary?.gainers ?? 0} / ${payload.summary?.losers ?? 0}`}
              tone="text-rose-400"
            />
            <MetricTile
              label="Average change"
              value={payload.summary ? formatPercent(payload.summary.average_change_percent) : "-"}
              tone={payload.summary?.average_change_percent >= 0 ? "text-rose-400" : "text-sky-400"}
            />
            <MetricTile label="Currency" value={payload.market?.currency_code ?? "-"} />
          </div>

          <div className="border-b border-slate-800 px-4 py-4">
            <div className="grid gap-4 xl:grid-cols-[1.4fr_1fr_1fr]">
              <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
                <div className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Session status</div>
                <div className="mt-2 text-sm text-slate-200">{payload.message}</div>
                <div className="mt-3 text-xs text-slate-500">
                  Last crawl: {payload.summary?.last_crawl_timestamp ?? "No dataset yet"}
                </div>
                {error ? <div className="mt-3 text-sm text-rose-400">{error}</div> : null}
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
                <div className="mb-3 text-[11px] uppercase tracking-[0.18em] text-slate-500">Top gainers</div>
                <div className="space-y-2">
                  {topGainers.map((row) => (
                    <div key={`gain-${getSymbolText(row)}`} className="flex items-center justify-between text-sm">
                      <div>
                        <div className="font-medium text-slate-100">{getSymbolText(row)}</div>
                        <div className="text-xs text-slate-500">{row.company_name}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium text-rose-400">{formatPercent(row.change_percent)}</div>
                        <div className="text-xs text-slate-500">
                          {currencySymbol}
                          {formatNumber(row.current_price, 2)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
                <div className="mb-3 text-[11px] uppercase tracking-[0.18em] text-slate-500">Top losers</div>
                <div className="space-y-2">
                  {topLosers.map((row) => (
                    <div key={`lose-${getSymbolText(row)}`} className="flex items-center justify-between text-sm">
                      <div>
                        <div className="font-medium text-slate-100">{getSymbolText(row)}</div>
                        <div className="text-xs text-slate-500">{row.company_name}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium text-sky-400">{formatPercent(row.change_percent)}</div>
                        <div className="text-xs text-slate-500">
                          {currencySymbol}
                          {formatNumber(row.current_price, 2)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-3 border-b border-slate-800 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-slate-500">
              <span>Filters</span>
              <span className="rounded-md border border-slate-800 bg-slate-950/70 px-2 py-1 text-[10px]">
                Most active
              </span>
              <span className="rounded-md border border-slate-800 bg-slate-950/70 px-2 py-1 text-[10px]">
                Top 50
              </span>
            </div>
            <div className="w-full lg:max-w-sm">
              <input
                type="text"
                value={filterText}
                onChange={(event) => setFilterText(event.target.value)}
                placeholder="Search ticker or company"
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-sky-500"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full border-collapse">
              <thead className="bg-slate-950/80 text-left text-[11px] uppercase tracking-[0.18em] text-slate-500">
                <tr>
                  <th className="border-b border-slate-800 px-4 py-3 font-medium">Symbol</th>
                  <th className="border-b border-slate-800 px-4 py-3 font-medium">Price * Vol</th>
                  <th className="border-b border-slate-800 px-4 py-3 font-medium">Price</th>
                  <th className="border-b border-slate-800 px-4 py-3 font-medium">Change %</th>
                  <th className="border-b border-slate-800 px-4 py-3 font-medium">Volume</th>
                  <th className="border-b border-slate-800 px-4 py-3 font-medium">Market</th>
                  <th className="border-b border-slate-800 px-4 py-3 font-medium">Rank</th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((row, index) => (
                  <tr
                    key={`${getSymbolText(row)}-${index}`}
                    className="border-b border-slate-900 text-sm text-slate-200 transition hover:bg-slate-900/70"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-800 text-xs font-semibold text-slate-300">
                          {getSymbolText(row).slice(0, 2)}
                        </div>
                        <div>
                          <div className="font-medium text-slate-50">{getSymbolText(row)}</div>
                          <div className="text-xs text-slate-500">{row.company_name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-300">
                      {currencySymbol}
                      {formatCompact(row.turnover)}
                    </td>
                    <td className="px-4 py-3 font-medium text-slate-50">
                      {currencySymbol}
                      {formatNumber(row.current_price, row.quote_currency === "KRW" ? 0 : 2)}
                    </td>
                    <td className={`px-4 py-3 font-medium ${getChangeTone(row.change_percent)}`}>
                      {formatPercent(row.change_percent)}
                    </td>
                    <td className="px-4 py-3 text-slate-300">{formatCompact(row.volume)}</td>
                    <td className="px-4 py-3 text-slate-500">{row.market}</td>
                    <td className="px-4 py-3 text-slate-500">{row.rank}</td>
                  </tr>
                ))}
                {filteredRows.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-4 py-8 text-center text-sm text-slate-500">
                      No rows match the current filter.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}

export default App;
