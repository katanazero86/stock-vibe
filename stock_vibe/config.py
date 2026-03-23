from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass(frozen=True, slots=True)
class MarketConfig:
    key: str
    label: str
    short_label: str
    region_label: str
    currency_code: str
    target_url: str


MARKETS: dict[str, MarketConfig] = {
    "us": MarketConfig(
        key="us",
        label="NASDAQ",
        short_label="NASDAQ",
        region_label="Most active NASDAQ stocks",
        currency_code="USD",
        target_url="https://www.tradingview.com/markets/stocks-usa/market-movers-active/",
    ),
    "kospi": MarketConfig(
        key="kospi",
        label="KOSPI",
        short_label="South Korea",
        region_label="Most active KOSPI stocks",
        currency_code="KRW",
        target_url="https://kr.tradingview.com/markets/stocks-korea/market-movers-active/",
    ),
}


@dataclass(slots=True)
class AppConfig:
    market_key: str = os.getenv("STOCK_VIBE_DEFAULT_MARKET", "us")
    top_n: int = int(os.getenv("STOCK_VIBE_TOP_N", "50"))
    max_retries: int = int(os.getenv("STOCK_VIBE_MAX_RETRIES", "3"))
    base_backoff_seconds: float = float(os.getenv("STOCK_VIBE_BACKOFF_SECONDS", "2"))
    action_jitter_seconds: float = float(os.getenv("STOCK_VIBE_JITTER_SECONDS", "0.6"))
    page_timeout_ms: int = int(os.getenv("STOCK_VIBE_PAGE_TIMEOUT_MS", "45000"))
    headless: bool = os.getenv("STOCK_VIBE_HEADLESS", "true").lower() != "false"
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("STOCK_VIBE_DATA_DIR", "data")))

    def ensure_directories(self) -> None:
        for path in (self.session_state_path, self.dataset_path, self.log_path):
            path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def market(self) -> MarketConfig:
        if self.market_key not in MARKETS:
            raise KeyError(f"Unsupported market: {self.market_key}")
        return MARKETS[self.market_key]

    @property
    def target_url(self) -> str:
        return self.market.target_url

    @property
    def session_state_path(self) -> Path:
        return self.data_dir / f"{self.market.key}-storage-state.json"

    @property
    def dataset_path(self) -> Path:
        return self.data_dir / f"{self.market.key}-latest-market-snapshot.csv"

    @property
    def log_path(self) -> Path:
        return self.data_dir / f"{self.market.key}-crawl-log.json"


def list_market_options() -> list[dict[str, str]]:
    return [
        {
            "key": market.key,
            "label": market.label,
            "short_label": market.short_label,
            "region_label": market.region_label,
            "currency_code": market.currency_code,
            "target_url": market.target_url,
        }
        for market in MARKETS.values()
    ]
