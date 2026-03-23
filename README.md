# Stock Vibe

Stock Vibe is a TradingView-based stock screener dashboard.
It crawls market data with Playwright, exposes the result through a Python API, and renders the UI with React + TailwindCSS.

## Overview

Supported views:
- `us`: NASDAQ-only view
- `kospi`: KOSPI-only view

Tracked fields:
- symbol
- company name
- current price
- change percent
- volume
- turnover-like `Price * Vol`
- crawl timestamp

## Crawl Source

The crawler reads TradingView "Most Active" pages:

- US source page:
  - [https://www.tradingview.com/markets/stocks-usa/market-movers-active/](https://www.tradingview.com/markets/stocks-usa/market-movers-active/)
- Korea source page:
  - [https://kr.tradingview.com/markets/stocks-korea/market-movers-active/](https://kr.tradingview.com/markets/stocks-korea/market-movers-active/)

Applied scope rules:
- `us` keeps only rows whose `data-rowkey` starts with `NASDAQ:`
- `kospi` keeps only symbols that exist in the official KRX KOSPI listed-company roster
- `kospi` company names are enriched with Korean names from KRX metadata

## Architecture

- `stock_vibe/`
  - crawler
  - parsing and normalization
  - KRX metadata enrichment
  - CSV cache storage
  - FastAPI backend
- `frontend/`
  - React app
  - TailwindCSS styling
  - market selector for `NASDAQ` and `KOSPI`
- `data/`
  - per-market CSV cache
  - per-market crawl log
  - per-market Playwright storage state

## Requirements

- Python `3.13+`
- Node.js `22+`
- npm
- Playwright Chromium

## Setup

Backend:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python -m playwright install chromium
```

Frontend:

```bash
cd frontend
npm install
cd ..
```

## Run

Start the backend:

```bash
python -m uvicorn stock_vibe.api:app --reload
```

Backend URL:
- [http://localhost:8000](http://localhost:8000)

Start the frontend in a second terminal:

```bash
cd frontend
npm run dev
```

Frontend URL:
- [http://localhost:5173](http://localhost:5173)

## Build

Frontend production build:

```bash
cd frontend
npm run build
```

## How It Works

1. The frontend requests a market view from the backend.
2. The backend opens the corresponding TradingView page with Playwright.
3. The crawler extracts table rows from the TradingView screener.
4. Exchange-specific filtering is applied:
   - NASDAQ-only for `us`
   - KOSPI-only for `kospi`
5. KOSPI company names are replaced with Korean names from KRX metadata.
6. The latest successful result is stored in a per-market CSV cache.
7. If live crawling fails, the backend falls back to the latest successful cache when available.

## API

Healthcheck:

```http
GET /api/health
```

Supported markets:

```http
GET /api/markets
```

Read cached snapshot:

```http
GET /api/snapshot?market=us
GET /api/snapshot?market=kospi
```

Refresh from TradingView:

```http
POST /api/refresh?market=us
POST /api/refresh?market=kospi
```

## Environment Variables

Backend:

- `STOCK_VIBE_DEFAULT_MARKET`
  - default market key
  - `us` or `kospi`
- `STOCK_VIBE_TOP_N`
  - target number of rows to keep
  - default: `50`
- `STOCK_VIBE_MAX_RETRIES`
  - crawl retry count
- `STOCK_VIBE_BACKOFF_SECONDS`
  - retry backoff base
- `STOCK_VIBE_JITTER_SECONDS`
  - random delay between critical actions
- `STOCK_VIBE_PAGE_TIMEOUT_MS`
  - Playwright page timeout
- `STOCK_VIBE_HEADLESS`
  - set to `false` to watch the browser
- `STOCK_VIBE_DATA_DIR`
  - directory for cache, logs, and storage state

Frontend:

- `VITE_API_BASE_URL`
  - default: `http://localhost:8000`

## Data Files

Generated under `data/`:

- `data/us-latest-market-snapshot.csv`
- `data/us-crawl-log.json`
- `data/us-storage-state.json`
- `data/kospi-latest-market-snapshot.csv`
- `data/kospi-crawl-log.json`
- `data/kospi-storage-state.json`
- `data/kospi-company-map.json`

Legacy single-market files may still exist:

- `data/latest_market_snapshot.csv`
- `data/crawl_log.json`
- `data/tradingview-storage-state.json`

Current code uses the per-market files first.

## Project Structure

```text
stock-vibe/
├─ stock_vibe/
│  ├─ api.py
│  ├─ config.py
│  ├─ crawler.py
│  ├─ market_metadata.py
│  ├─ models.py
│  ├─ parsing.py
│  ├─ service.py
│  └─ storage.py
├─ frontend/
│  ├─ src/
│  ├─ package.json
│  └─ tailwind.config.js
├─ data/
├─ memory-bank/
├─ pyproject.toml
└─ README.md
```

## Notes

- TradingView DOM changes may require selector updates.
- The crawler uses retry, backoff, session reuse, and jitter to reduce friction.
- The crawler does not rely on CAPTCHA solving or aggressive anti-bot circumvention.
- KOSPI company names are enriched from KRX metadata.
- KOSPI ticker codes are kept as strings so leading zeros are preserved.
- The current TradingView country-level pages do not expose dedicated exchange-only URLs directly, so exchange scope is enforced after extraction.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python -m playwright install chromium
cd frontend
npm install
cd ..
python -m uvicorn stock_vibe.api:app --reload
```

Then in a second terminal:

```bash
cd frontend
npm run dev
```
