# PRD: TradingView Volume Leaders Dashboard

## 1. Product Summary
- Build a local dashboard that crawls stock market data from TradingView using Playwright MCP, exposes it through a Python API, and visualizes it with React + TailwindCSS.
- The first release focuses on the top 50 stocks ranked by trading volume for US stocks and KOSPI.
- For each stock, the system must collect the current price and the day-over-day percentage change.

## 2. Goal
- Provide a fast, readable view of the most actively traded stocks.
- Reduce manual checking of TradingView tables.
- Create a base architecture that can later expand to more metrics and markets.

## 3. Non-Goals
- Real-time tick-level streaming.
- Order execution or brokerage integration.
- Historical backtesting in the first release.
- Multi-source price reconciliation in the first release.

## 4. Primary User
- A single operator or analyst running the app locally.
- The user wants a quick view of high-volume movers without manually browsing TradingView.

## 5. Core User Flow
1. User launches the local frontend and Python API.
2. User triggers a crawl or uses the latest cached crawl result.
3. System opens TradingView through Playwright MCP.
4. System extracts the top 50 stocks by trading volume for the selected market.
5. System normalizes and stores symbol, company name if available, current price, change percent, rank, and crawl timestamp.
6. React renders a dashboard table and summary visualizations using the Python API.
7. User sorts, filters, and inspects the market snapshot.

## 6. Functional Requirements

### 6.1 Crawling
- The system must use Playwright MCP for browser automation.
- The crawl target is a TradingView market screener or equivalent page that exposes stocks ranked by trading volume.
- The first release must support these market pages:
  - US stocks most active
  - KOSPI most active
- The system must fetch exactly the top 50 rows from the ranked result set.
- The crawler must extract:
  - rank
  - ticker or symbol
  - company name when available
  - current price
  - day-over-day change percent
  - volume or traded value field used for ranking, when available
  - crawl timestamp
- The crawler must handle page load latency and dynamic rendering.
- The crawler should fail clearly when selectors no longer match.

### 6.1.1 Crawl Blocking Mitigation
- The system must be designed to reduce the likelihood of crawl blocking during browser automation.
- The crawler should prefer stable, low-frequency access patterns over aggressive repeated requests.
- The crawler should support bounded retries with backoff when page load or data extraction fails temporarily.
- The crawler should support session reuse when appropriate so repeated runs do not always start from a cold browser state.
- The crawler should support configurable wait strategies and jitter between critical actions to avoid burst-like behavior.
- The crawler should avoid unnecessary navigation, reloads, and duplicate requests during a single crawl cycle.
- If TradingView presents a hard block, consent screen, or CAPTCHA, the system must stop automated extraction and surface the state clearly to the operator.
- The first release must not depend on CAPTCHA solving or unsupported circumvention techniques.
- Blocking mitigation assumptions and chosen tactics must be documented in `memory-bank/decisions.md`.

### 6.2 Data Handling
- Normalize numeric fields into machine-readable values.
- Preserve the raw crawl timestamp in local time.
- Save the latest dataset locally in a simple format such as CSV or JSON.
- The app should avoid duplicate ambiguity by storing one row per symbol per crawl timestamp.

### 6.3 Dashboard
- Build the UI in React with TailwindCSS.
- Display a main table for the top 50 stocks.
- Provide sorting and filtering by:
  - rank
  - symbol
  - current price
  - change percent
- Show at least the following summary views:
  - gainers vs losers count
  - top positive movers
  - top negative movers
- Show the last crawl time clearly.
- Provide a manual refresh action.
- The frontend must fetch cached data and trigger live refreshes via the Python API.
- The frontend must allow switching between US stocks and KOSPI from the UI.

## 7. Data Source Requirements
- Primary source is TradingView only for v1.
- Ranking basis is trading volume, subject to what TradingView exposes on the target screener page.
- If TradingView exposes a closely related ranking field instead of a plain volume field, that choice must be documented in `memory-bank/decisions.md`.

## 8. UX Requirements
- The dashboard should be readable on a standard desktop browser.
- Positive and negative change percentages must be visually distinct.
- Users should understand the data freshness immediately.
- Errors must be shown in plain language with probable cause when crawling fails.
- The frontend should remain usable when the latest live refresh falls back to cached data.
- The visual language should reference TradingView stock screener patterns such as a compact dark toolbar, market tabs, and dense data table presentation.

## 9. Technical Requirements
- Language: Python.
- API framework: Python HTTP API.
- UI framework: React.
- Styling: TailwindCSS.
- Browser automation: Playwright MCP.
- Project should support local execution with a straightforward setup.
- Code should separate crawling, parsing, storage, API, and presentation concerns.
- Crawling behavior such as retry count, backoff timing, session persistence, and wait intervals should be configurable.

## 10. Reliability Requirements
- The app should tolerate temporary page delays through bounded waits and retryable steps.
- Selector assumptions must be documented and easy to update.
- When crawl fails, the dashboard should keep showing the most recent successful dataset if one exists.
- The crawler should degrade safely under anti-bot friction by slowing down, retrying within limits, or falling back to the most recent successful dataset.
- The system should log whether a failure appears to be selector drift, temporary load failure, or probable crawl blocking.

## 11. Success Metrics
- Top 50 volume-ranked stocks are loaded successfully in a single run.
- Required fields are populated for at least 95 percent of rows in normal conditions.
- Dashboard renders within an acceptable local interactive time after crawl completion.
- A developer can update selectors without changing unrelated dashboard logic.

## 12. Risks
- TradingView DOM structure may change.
- Some fields may render differently by locale or market selection.
- Anti-bot or rate-limit behavior may affect crawl stability.
- Volume ranking interpretation may differ across screener pages or regions.
- Repeated local test runs may trigger temporary access friction if crawl cadence is too aggressive.

## 13. Open Questions
- Which market universe should v1 target: US, Korea, or another exchange set?
- Which exact TradingView screener URL should be used?
- Should local persistence be CSV, JSON, or SQLite for v1?
- Is manual refresh enough for v1, or should scheduled refresh be added next?

## 14. Initial Delivery Scope
- Local Python API backend.
- Local React dashboard frontend.
- Market selector for US stocks and KOSPI.
- Manual crawl trigger.
- TradingView top 50 by trading volume crawl.
- Current price and day-over-day change percent extraction.
- Basic local persistence.
- Summary metrics and sortable table.
- Initial blocking-mitigation controls such as bounded retry, session reuse, configurable waits, and cached fallback behavior.
