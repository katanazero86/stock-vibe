from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import random
import time

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from stock_vibe.config import AppConfig
from stock_vibe.market_metadata import load_kospi_company_map
from stock_vibe.models import StockSnapshot
from stock_vibe.parsing import parse_compact_number, parse_currency, parse_percent


BLOCK_INDICATORS = (
    "captcha",
    "verify you are human",
    "access denied",
    "unusual traffic",
    "blocked",
)


class CrawlError(RuntimeError):
    """Raised when crawling fails in a recoverable or terminal way."""


@dataclass(slots=True)
class CrawlResult:
    snapshots: list[StockSnapshot]
    from_cache: bool = False


class TradingViewCrawler:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def fetch_top_volume_stocks(self) -> list[StockSnapshot]:
        last_error: Exception | None = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                return self._fetch_once()
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt == self.config.max_retries:
                    break
                delay = self.config.base_backoff_seconds * attempt + random.uniform(
                    0,
                    self.config.action_jitter_seconds,
                )
                time.sleep(delay)
        raise CrawlError(f"Failed to crawl TradingView after {self.config.max_retries} attempts: {last_error}")

    def _fetch_once(self) -> list[StockSnapshot]:
        now = datetime.now().isoformat(timespec="seconds")
        self.config.ensure_directories()
        extraction_limit = max(self.config.top_n * 40, 1_500)
        kospi_company_map: dict[str, str] = {}
        if self.config.market.key == "kospi":
            kospi_company_map = load_kospi_company_map(self.config.data_dir / "kospi-company-map.json")

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=self.config.headless)
            context_kwargs: dict[str, object] = {
                "locale": "ko-KR" if self.config.market.key == "kospi" else "en-US",
                "viewport": {"width": 1440, "height": 1200},
                "user_agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
            }
            if self.config.session_state_path.exists():
                context_kwargs["storage_state"] = str(self.config.session_state_path)

            context = browser.new_context(**context_kwargs)
            page = context.new_page()
            page.set_default_timeout(self.config.page_timeout_ms)

            try:
                self._wait_with_jitter()
                page.goto(self.config.target_url, wait_until="domcontentloaded")
                self._wait_with_jitter()
                page.wait_for_selector("table tbody tr", timeout=self.config.page_timeout_ms)
                self._raise_if_blocked(page)
                rows = page.evaluate(
                    """
                    (topN) => {
                      const rows = Array.from(document.querySelectorAll('table tbody tr')).slice(0, topN);
                      return rows.map((row, index) => {
                        const cells = row.querySelectorAll('td');
                        const links = row.querySelectorAll('a');
                        return {
                          rank: index + 1,
                          rowKey: row.getAttribute('data-rowkey') || '',
                          symbol: links[0]?.textContent?.trim() || '',
                          companyName: links[1]?.textContent?.trim() || '',
                          turnoverText: cells[1]?.textContent?.trim() || '',
                          priceText: cells[2]?.textContent?.trim() || '',
                          changeText: cells[3]?.textContent?.trim() || '',
                          volumeText: cells[4]?.textContent?.trim() || '',
                        };
                      });
                    }
                    """,
                    extraction_limit,
                )
            except PlaywrightTimeoutError as exc:
                raise CrawlError("TradingView table did not become available in time.") from exc
            finally:
                context.storage_state(path=str(self.config.session_state_path))
                context.close()
                browser.close()

        snapshots: list[StockSnapshot] = []
        for row in rows:
            symbol = row["symbol"].strip()
            if not symbol:
                continue
            if self.config.market.key == "us" and not row["rowKey"].startswith("NASDAQ:"):
                continue
            if self.config.market.key == "kospi" and symbol not in kospi_company_map:
                continue
            market = row["rowKey"].split(":", maxsplit=1)[0] if row["rowKey"] else ""
            current_price = parse_currency(row["priceText"])
            change_percent = parse_percent(row["changeText"])
            if current_price is None or change_percent is None:
                continue
            company_name = row["companyName"].strip() or symbol
            if self.config.market.key == "kospi":
                company_name = kospi_company_map.get(symbol, company_name)
            snapshots.append(
                StockSnapshot(
                    rank=int(row["rank"]),
                    symbol=symbol,
                    company_name=company_name,
                    current_price=current_price,
                    change_percent=change_percent,
                    volume=parse_compact_number(row["volumeText"]),
                    turnover=parse_compact_number(row["turnoverText"]),
                    market=market,
                    quote_currency=self.config.market.currency_code,
                    source_url=self.config.target_url,
                    crawl_timestamp=now,
                )
            )

        if len(snapshots) < min(self.config.top_n, 10):
            raise CrawlError(
                f"TradingView returned too few parsable rows ({len(snapshots)}). "
                "This may indicate selector drift or blocking."
            )
        trimmed = snapshots[: self.config.top_n]
        for index, snapshot in enumerate(trimmed, start=1):
            snapshot.rank = index
        return trimmed

    def _wait_with_jitter(self) -> None:
        time.sleep(random.uniform(0.2, self.config.action_jitter_seconds))

    def _raise_if_blocked(self, page) -> None:
        body_text = page.locator("body").inner_text(timeout=5_000).lower()
        if any(indicator in body_text for indicator in BLOCK_INDICATORS):
            raise CrawlError("TradingView appears to be showing a block or human-verification screen.")
