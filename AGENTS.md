# AGENTS.md

## Purpose
- Build a stock market dashboard that crawls market data with Playwright MCP and visualizes it with Streamlit.
- Treat `memory-bank` as the source of truth for product intent, scope, and execution context.

## Working Rules
- Read the relevant files in `memory-bank/` before starting implementation.
- Update `memory-bank/` whenever requirements, assumptions, scope, architecture, or execution status changes.
- Do not let code changes drift away from `memory-bank`; update the docs first or in the same change set.
- Keep entries concise, explicit, and implementation-oriented.

## Required Memory Bank Files
- `memory-bank/PRD.md`: product requirements, user flows, scope, constraints, success criteria.
- `memory-bank/progress.md`: current status, completed work, next steps, blockers.
- `memory-bank/decisions.md`: architectural and product decisions with rationale.

## Update Triggers
- New data source, crawling rule, selector strategy, or anti-breakage approach added.
- Streamlit dashboard structure or UX flow changes.
- TradingView extraction scope changes, including symbol universe or ranking logic.
- Environment setup, run commands, or deployment assumptions change.
- A task is completed, blocked, or reprioritized.

## Implementation Expectations
- Use Playwright MCP for browser-driven TradingView data extraction.
- Capture the top 50 stocks by trading volume and store at minimum:
  - company or symbol
  - current price
  - day-over-day change percent
  - crawl timestamp
- Visualize the crawled dataset in Streamlit with clear sorting and filtering.
- Prefer resilient selectors and document fallback strategies in `memory-bank/decisions.md`.

## Definition of Done
- Relevant `memory-bank` documents are updated.
- Product and technical assumptions are explicit.
- Implementation work can proceed without re-discovering core requirements.
