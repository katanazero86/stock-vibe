from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from stock_vibe.config import AppConfig
from stock_vibe.crawler import CrawlError, TradingViewCrawler
from stock_vibe.storage import SnapshotStorage


@dataclass(slots=True)
class DashboardData:
    frame: pd.DataFrame | None
    source: str
    message: str


class DashboardService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.storage = SnapshotStorage(config.dataset_path, config.log_path)
        self.crawler = TradingViewCrawler(config)

    def refresh(self) -> DashboardData:
        try:
            snapshots = self.crawler.fetch_top_volume_stocks()
            frame = self.storage.save(snapshots)
            return DashboardData(frame=frame, source="live", message=f"Fetched {len(frame)} rows from TradingView.")
        except CrawlError as exc:
            self.storage.log_failure("crawl_error", str(exc))
            cached = self.storage.load_latest()
            if cached is not None and not cached.empty:
                return DashboardData(
                    frame=cached,
                    source="cache",
                    message=f"{exc} Showing the most recent cached dataset instead.",
                )
            return DashboardData(frame=None, source="error", message=str(exc))

    def load_cached(self) -> DashboardData:
        cached = self.storage.load_latest()
        if cached is None or cached.empty:
            return DashboardData(frame=None, source="empty", message="No cached dataset is available yet.")
        return DashboardData(frame=cached, source="cache", message=f"Loaded {len(cached)} cached rows.")
