# Decisions

## Initial Decisions
- Use `memory-bank` as the working memory and documentation source of truth.
- Use Playwright MCP for TradingView crawling.
- Replace Streamlit with a Python API backend plus a React + TailwindCSS frontend.
- Scope v1 to the top 50 stocks ranked by trading volume.
- Required v1 metrics are current price and day-over-day change percent.
- Treat crawl blocking as a first-class reliability concern and address it with conservative automation patterns rather than aggressive circumvention.
- Use the public TradingView page `https://www.tradingview.com/markets/stocks-usa/market-movers-active/` as the initial target during implementation.
- Add a second target page for KOSPI at `https://kr.tradingview.com/markets/stocks-korea/market-movers-active/`.
- Persist the latest successful crawl to a local CSV file and keep a small JSON crawl log for failure/success history.
- Persist crawl cache, log, and browser session state separately for each market.
- Separate responsibilities into config, crawler, parsing, storage, service, API, and frontend modules.
- Reuse browser session state between runs via a Playwright storage state file to reduce cold-start friction.
- Align the frontend visual language with TradingView's screener layout instead of a card-first dashboard look.
- Enforce NASDAQ scope by filtering TradingView US rows to those whose `data-rowkey` starts with `NASDAQ:`.
- Enforce KOSPI scope by filtering TradingView Korea rows against the official KRX KOSPI listed-company roster.
- Use KRX company metadata to show Korean company names for the KOSPI view.

## Pending Decisions
- Selector fallback strategy after validating the target page structure.
- Exact session persistence and retry/backoff policy for TradingView crawling.
- Whether the frontend should remain a client-rendered Vite app or move to a React framework later.
